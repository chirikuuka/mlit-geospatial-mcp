import json
import logging
import uuid

"""
MCPサーバーのエントリポイント。
ツールのリスト取得やツール呼び出しのハンドラを提供する。
"""

from resources import PROMPTS, RESOURCES, build_prompt, build_resource_contents
from request_processor.handler import handle_request
from tools import API_SPECS, TOOLS
from utils.payload import build_payload

import anyio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from request_processor.handler import handle_request
from tools import API_SPECS, TOOLS
from utils.payload import build_payload

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


server = Server("mlit-geospatial-mcp")


def _build_resource_error_contents(
    requested_uri: str, error_message: str
) -> list[types.TextResourceContents]:
    body = {
        "status": "error",
        "error": error_message,
        "requested_uri": requested_uri,
        "available_resources": [str(resource.uri) for resource in RESOURCES],
    }
    return [
        types.TextResourceContents(
            uri=requested_uri,
            mimeType="application/json",
            text=json.dumps(body, ensure_ascii=False, indent=2),
        )
    ]


def _build_prompt_error_result(
    requested_name: str, error_message: str
) -> types.GetPromptResult:
    available_prompts = [prompt.name for prompt in PROMPTS]
    return types.GetPromptResult(
        description="指定された prompt は見つかりませんでした。",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=(
                        f"{error_message}\n"
                        f"requested_name: {requested_name}\n"
                        f"available_prompts: {', '.join(available_prompts)}"
                    ),
                ),
            )
        ],
    )


@server.list_tools()
async def handle_list_tools():
    """
    利用可能なツール一覧を取得する。

    Returns:
        TOOLS:ツール定義のリスト
    """
    return TOOLS


@server.list_resources()
async def handle_list_resources():
    """
    利用可能なリソース一覧を取得する。

    Returns:
        RESOURCES: リソース定義のリスト
    """
    return RESOURCES


@server.read_resource()
async def handle_read_resource(uri: str):
    """
    リソースURIに対応する本文を取得する。

    Args:
        uri(str): 取得対象のリソースURI

    Returns:
        list[TextResourceContents]: リソース本文
    """
    try:
        return build_resource_contents(uri)
    except ValueError as exc:
        logger.warning(f"Unknown resource requested: {uri}")
        return _build_resource_error_contents(uri, str(exc))


@server.list_prompts()
async def handle_list_prompts():
    """
    利用可能なプロンプト一覧を取得する。

    Returns:
        PROMPTS: プロンプト定義のリスト
    """
    return PROMPTS


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None = None):
    """
    プロンプト名に対応するプロンプト本文を取得する。

    Args:
        name(str): 取得対象のプロンプト名
        arguments(dict | None): プロンプト引数

    Returns:
        GetPromptResult: プロンプト本文
    """
    try:
        return build_prompt(name, arguments)
    except ValueError as exc:
        logger.warning(f"Unknown prompt requested: {name}")
        return _build_prompt_error_result(name, str(exc))


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Claudから呼び出されたtoolを実行する。
    tool名からAPI_SPECを取得し、引数をAPI用のpayloadに変換後、
    handle_request（内部処理）に渡す。
    結果をJSONとして返却。

    Args:
        name(str):呼び出されたtool名
        arguments(dict):toolに渡された引数

    Returns:
        list[TextContent]: 実行結果（JSON文字列）
    """
    rid = uuid.uuid4().hex
    logger.info(f"Tool called: {name} (request_id: {rid})")

    spec = API_SPECS[name]
    payload = build_payload(
        spec=spec,
        args=arguments,
    )
    logger.info(f"payload:{payload}")
    result = await handle_request(payload)
    return [
        types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2),
        )
    ]


async def _main() -> None:
    """
    MCPサーバーのメイン処理。
    イベントループを実行する。
    """
    async with stdio_server() as (read, write):
        caps = server.get_capabilities(
            notification_options=NotificationOptions(), experimental_capabilities={}
        )

        init_opts = InitializationOptions(
            server_name="mlit-geospatial-mcp", server_version="0.1.0", capabilities=caps
        )

        logger.info("MCP server starting...")
        await server.run(read, write, init_opts)


if __name__ == "__main__":
    anyio.run(_main)
