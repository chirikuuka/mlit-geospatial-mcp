interface ContainerStub {
  fetch(request: Request): Response | Promise<Response>;
}

interface ContainerNamespace {
  getByName(name: string): ContainerStub;
}

interface RateLimiter {
  limit(options: { key: string }): Promise<{ success: boolean }>;
}

export interface Env {
  MLIT_GEOSPATIAL_CONTAINER: ContainerNamespace;
  MCP_RATE_LIMITER: RateLimiter;
  LIBRARY_API_KEY?: string;
  MCP_PATH_TOKEN?: string;
}

const encoder = new TextEncoder();

/** 秘密URLと回数制限で保護してからMCP Containerへ転送する。 */
export async function handleRequest(request: Request, env: Env): Promise<Response> {
  if (!env.MCP_PATH_TOKEN || !env.LIBRARY_API_KEY) {
    return notFound();
  }

  const url = new URL(request.url);
  const match = /^\/([^/]+)\/(mcp|health)$/u.exec(url.pathname);
  if (!match || !constantTimeEqual(match[1], env.MCP_PATH_TOKEN)) {
    return notFound();
  }

  let allowed: boolean;
  try {
    ({ success: allowed } = await env.MCP_RATE_LIMITER.limit({
      key: "mlit-geospatial-mcp",
    }));
  } catch {
    return jsonResponse({ error: "Rate limiter unavailable" }, {
      status: 503,
      headers: { "Retry-After": "60" },
    });
  }

  if (!allowed) {
    return jsonResponse({ error: "Too many requests" }, {
      status: 429,
      headers: { "Retry-After": "60" },
    });
  }

  url.pathname = `/${match[2]}`;
  const forwardedRequest = new Request(url, request);
  return env.MLIT_GEOSPATIAL_CONTAINER.getByName("main").fetch(forwardedRequest);
}

function constantTimeEqual(candidate: string, expected: string): boolean {
  const candidateBytes = encoder.encode(candidate);
  const expectedBytes = encoder.encode(expected);
  let difference = candidateBytes.length ^ expectedBytes.length;

  for (let index = 0; index < expectedBytes.length; index += 1) {
    difference |= expectedBytes[index] ^ (candidateBytes[index] ?? 0);
  }

  return difference === 0;
}

function notFound(): Response {
  return new Response("not found", {
    status: 404,
    headers: {
      "Cache-Control": "no-store",
      "Content-Type": "text/plain; charset=UTF-8",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function jsonResponse(body: unknown, init: ResponseInit): Response {
  const headers = new Headers(init.headers);
  headers.set("Cache-Control", "no-store");
  headers.set("Content-Type", "application/json; charset=UTF-8");
  headers.set("X-Content-Type-Options", "nosniff");
  return new Response(JSON.stringify(body), { ...init, headers });
}
