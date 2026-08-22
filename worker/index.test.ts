import { describe, expect, it, vi } from "vitest";

import { handleRequest, type Env } from "./handler";

function makeEnv(options: {
  token?: string;
  apiKey?: string;
  allowed?: boolean;
  limiterError?: Error;
} = {}) {
  const fetch = vi.fn(async (_request: Request) => new Response("forwarded", { status: 202 }));
  const getByName = vi.fn((_name: string) => ({ fetch }));
  const limit = options.limiterError
    ? vi.fn(async () => { throw options.limiterError; })
    : vi.fn(async () => ({ success: options.allowed ?? true }));

  return {
    env: {
      MLIT_GEOSPATIAL_CONTAINER: { getByName },
      MCP_RATE_LIMITER: { limit },
      LIBRARY_API_KEY: options.apiKey ?? "library-key",
      MCP_PATH_TOKEN: options.token ?? "secret-token",
    } as unknown as Env,
    fetch,
    getByName,
    limit,
  };
}

describe("handleRequest", () => {
  it("returns 404 when a required secret is missing", async () => {
    const { env, getByName, limit } = makeEnv({ apiKey: "" });

    const response = await handleRequest(
      new Request("https://example.test/secret-token/mcp", { method: "POST" }),
      env,
    );

    expect(response.status).toBe(404);
    expect(getByName).not.toHaveBeenCalled();
    expect(limit).not.toHaveBeenCalled();
  });

  it("returns 404 for an invalid capability URL", async () => {
    const { env, getByName, limit } = makeEnv();

    const response = await handleRequest(
      new Request("https://example.test/wrong/mcp", { method: "POST" }),
      env,
    );

    expect(response.status).toBe(404);
    expect(getByName).not.toHaveBeenCalled();
    expect(limit).not.toHaveBeenCalled();
  });

  it.each(["mcp", "health"])("forwards the protected %s path", async (path) => {
    const { env, fetch, getByName, limit } = makeEnv();
    const request = new Request(`https://example.test/secret-token/${path}`, {
      method: path === "mcp" ? "POST" : "GET",
    });

    const response = await handleRequest(request, env);

    expect(response.status).toBe(202);
    expect(limit).toHaveBeenCalledWith({ key: "mlit-geospatial-mcp" });
    expect(getByName).toHaveBeenCalledWith("main");
    const forwarded = fetch.mock.calls[0]![0];
    expect(new URL(forwarded.url).pathname).toBe(`/${path}`);
  });

  it("returns 429 when the rate limit is exceeded", async () => {
    const { env, getByName } = makeEnv({ allowed: false });

    const response = await handleRequest(
      new Request("https://example.test/secret-token/mcp", { method: "POST" }),
      env,
    );

    expect(response.status).toBe(429);
    expect(response.headers.get("Retry-After")).toBe("60");
    expect(getByName).not.toHaveBeenCalled();
  });

  it("fails closed when the rate limiter is unavailable", async () => {
    const { env, getByName } = makeEnv({ limiterError: new Error("unavailable") });

    const response = await handleRequest(
      new Request("https://example.test/secret-token/mcp", { method: "POST" }),
      env,
    );

    expect(response.status).toBe(503);
    expect(getByName).not.toHaveBeenCalled();
  });
});
