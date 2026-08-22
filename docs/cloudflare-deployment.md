# Cloudflare OS向けデプロイ

この構成は、元のPython MCPをCloudflare Containerで実行し、秘密URLを持つ
Streamable HTTP MCPとして公開する。

## セキュリティ境界

- `LIBRARY_API_KEY`はWorker Secretとして保存し、リポジトリへ書かない。
- `MCP_PATH_TOKEN`は64文字のランダムな16進数を使い、URL自体をアクセス権として扱う。
- MCPツールは読み取り専用で、Container内へのファイル保存を禁止する。
- 1回で指定できるAPIは6個まで、検索距離は425mまでに制限する。
- Cloudflare Rate Limitingで、1拠点あたり毎分60回までに制限する。

## 検証

```sh
uv sync --frozen
uv run pytest
pnpm install --frozen-lockfile
pnpm verify
```

Dockerが起動していることも確認する。

```sh
docker info
```

## 初回デプロイ

最初のデプロイではSecretが未設定のため、すべての公開リクエストが404になる。

```sh
pnpm run deploy
MCP_WORKER_HOST=<worker-name>.<workers-subdomain>.workers.dev pnpm run secrets:configure
```

macOSでは伏せ字の入力画面が開き、APIキーをCloudflare Secretへ設定する。
`MCP_PATH_TOKEN`は自動生成し、完成したMCP URLだけをmacOSキーチェーンへ保存する。

接続URLは次の形式になる。

```text
https://<worker-name>.<workers-subdomain>.workers.dev/<MCP_PATH_TOKEN>/mcp
```

Cloudflare OSの「外部サービス連携」で「Any MCP server」を選び、このURLを登録する。
将来追加されるツールへ自動で権限を広げないため、`get_multi_api`だけを名前で許可する。

PLATEAU MCPは別の接続として、次のURLを登録する。

```text
https://api.plateauview.mlit.go.jp/mcp
```

こちらも全ツール許可ではなく、必要な読み取り専用ツールを名前で選ぶ。

Rate Limitingの`namespace_id`はCloudflareアカウント内で一意にする必要がある。
`wrangler.jsonc`の値が既存Workerと重複する場合は、未使用の正の整数文字列へ変更する。
