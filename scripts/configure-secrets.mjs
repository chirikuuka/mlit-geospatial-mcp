import { randomBytes } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const workerHost = process.env.MCP_WORKER_HOST?.trim();
const keychainService = "mlit-geospatial-mcp";

if (!workerHost || workerHost.includes("://") || workerHost.includes("/")) {
  console.error(
    "MCP_WORKER_HOSTにデプロイ済みWorkerのホスト名を指定してください。",
  );
  process.exit(1);
}

const prompt = spawnSync(
  "osascript",
  [
    "-e",
    'display dialog "不動産情報ライブラリのAPIキーを入力してください。値は画面・ログ・リポジトリへ表示しません。" default answer "" with hidden answer buttons {"キャンセル", "設定"} default button "設定"',
    "-e",
    "text returned of result",
  ],
  { encoding: "utf8" },
);

if (prompt.status !== 0) {
  console.error("APIキーの設定をキャンセルしました。");
  process.exit(1);
}

const libraryApiKey = prompt.stdout.trim();
if (libraryApiKey.length < 8) {
  console.error("APIキーが空か、短すぎます。設定を中止しました。");
  process.exit(1);
}

const pathToken = randomBytes(32).toString("hex");
putWorkerSecret("LIBRARY_API_KEY", libraryApiKey);
putWorkerSecret("MCP_PATH_TOKEN", pathToken);

const endpoint = `https://${workerHost}/${pathToken}/mcp`;
storeInKeychain("MCP_URL", endpoint);

console.log("Cloudflare SecretとMCP接続URLを安全に設定しました。");
console.log(`接続URLはmacOSキーチェーンの「${keychainService} / MCP_URL」に保存しました。`);

function putWorkerSecret(name, value) {
  const result = spawnSync(
    "pnpm",
    ["exec", "wrangler", "secret", "put", name],
    {
      cwd: root,
      encoding: "utf8",
      env: {
        ...process.env,
        WRANGLER_LOG_PATH: join(root, ".wrangler", "wrangler.log"),
      },
      input: `${value}\n`,
    },
  );

  process.stdout.write(result.stdout.replaceAll(value, "[redacted]"));
  process.stderr.write(result.stderr.replaceAll(value, "[redacted]"));
  if (result.status !== 0) {
    console.error(`${name}の設定に失敗しました。`);
    process.exit(result.status ?? 1);
  }
}

function storeInKeychain(account, value) {
  const result = spawnSync(
    "security",
    [
      "add-generic-password",
      "-U",
      "-a",
      account,
      "-s",
      keychainService,
      "-w",
      value,
    ],
    { encoding: "utf8" },
  );
  if (result.status !== 0) {
    console.error("MCP接続URLのキーチェーン保存に失敗しました。");
    process.exit(result.status ?? 1);
  }
}
