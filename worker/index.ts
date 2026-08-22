import { Container } from "@cloudflare/containers";
import { env as workerEnv } from "cloudflare:workers";

import { handleRequest, type Env } from "./handler";

interface ContainerEnv {
  LIBRARY_API_KEY?: string;
}

const containerEnv = workerEnv as unknown as ContainerEnv;

/** Python MCPサーバーを実行するCloudflare Container。 */
export class MlitGeospatialContainer extends Container {
  defaultPort = 8080;
  sleepAfter = "10m";
  envVars = {
    LIBRARY_API_KEY: containerEnv.LIBRARY_API_KEY ?? "",
    LOG_LEVEL: "WARNING",
    MCP_TRANSPORT: "streamable-http",
    PYTHONUNBUFFERED: "1",
  };
}

export default {
  fetch: handleRequest,
} satisfies ExportedHandler<Env>;
