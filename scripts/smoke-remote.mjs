import { spawnSync } from "node:child_process";

const endpoint = readEndpoint();
const initialize = await callMcp(1, "initialize", {
  protocolVersion: "2025-06-18",
  capabilities: {},
  clientInfo: { name: "mlit-geospatial-smoke", version: "1.0.0" },
});

if (initialize.result?.serverInfo?.name !== "mlit-geospatial-mcp") {
  throw new Error("MCP initializeの応答が想定と異なります。");
}

const tools = await callMcp(2, "tools/list", {});
const catalog = tools.result?.tools;
if (!Array.isArray(catalog) || catalog.length !== 1) {
  throw new Error("MCPツール一覧を取得できませんでした。");
}
if (catalog[0].name !== "get_multi_api" || catalog[0].annotations?.readOnlyHint !== true) {
  throw new Error("読み取り専用ツールの定義が想定と異なります。");
}

const liveCall = await callMcp(3, "tools/call", {
  name: "get_multi_api",
  arguments: {
    lat: 36.6953,
    lon: 137.2113,
    target_apis: [4],
    distance: 100,
  },
});
if (liveCall.result?.isError === true) {
  throw new Error("不動産情報ライブラリAPIの実データ取得がエラーになりました。");
}
const liveText = liveCall.result?.content?.[0]?.text;
const liveData = typeof liveText === "string" ? JSON.parse(liveText) : undefined;
if (
  liveData?.status !== "success"
  || !Array.isArray(liveData?.data?.api_results)
  || liveData.data.api_results.every((result) => result === null)
) {
  throw new Error("不動産情報ライブラリAPIから実データを取得できませんでした。");
}

console.log("Remote MCP smoke test: OK");
console.log(`Server: ${initialize.result.serverInfo.name} ${initialize.result.serverInfo.version}`);
console.log("Tools: get_multi_api (read-only)");
console.log("Live API: 都市計画区域データの取得OK");

async function callMcp(id, method, params) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      Accept: "application/json, text/event-stream",
      "Content-Type": "application/json",
      "MCP-Protocol-Version": "2025-06-18",
    },
    body: JSON.stringify({ jsonrpc: "2.0", id, method, params }),
  });
  if (!response.ok) {
    throw new Error(`MCP ${method} failed: HTTP ${response.status}`);
  }
  return response.json();
}

function readEndpoint() {
  const result = spawnSync(
    "security",
    [
      "find-generic-password",
      "-w",
      "-a",
      "MCP_URL",
      "-s",
      "mlit-geospatial-mcp",
    ],
    { encoding: "utf8" },
  );
  if (result.status !== 0 || !result.stdout.trim()) {
    throw new Error("キーチェーンにMCP接続URLが見つかりません。先にsecrets:configureを実行してください。");
  }
  return result.stdout.trim();
}
