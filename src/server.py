"""MLIT geospatial MCP server entry point.

The original stdio transport remains available for local clients. Cloudflare
Containers use the stateless Streamable HTTP transport.
"""

from __future__ import annotations

import copy
import json
import logging
import os
import uuid
from collections.abc import Mapping
from typing import Any

import anyio
import mcp.types as types
import uvicorn
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from request_processor.handler import handle_request
from tools import API_SPECS, TOOLS
from utils.const import LIBRARY_API_KEY
from utils.payload import build_payload

SERVER_NAME = "mlit-geospatial-mcp"
SERVER_VERSION = "1.0.0"
MAX_APIS_PER_CALL = 6

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "WARNING").upper(), logging.WARNING)
)
logger = logging.getLogger(__name__)

def _remote_tools() -> list[types.Tool]:
    """Return a read-only catalog suitable for a remote MCP client."""
    tools = copy.deepcopy(TOOLS)
    for tool in tools:
        tool.annotations = types.ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
        properties = tool.input_schema.get("properties", {})
        if isinstance(properties, dict):
            properties.pop("save_file", None)
            properties.pop("output_dir", None)
            lat = properties.get("lat")
            lon = properties.get("lon")
            target_apis = properties.get("target_apis")
            if isinstance(lat, dict):
                lat.update({"minimum": -90, "maximum": 90})
            if isinstance(lon, dict):
                lon.update({"minimum": -180, "maximum": 180})
            if isinstance(target_apis, dict):
                target_apis.update(
                    {
                        "description": "呼び出すAPI番号。1〜30から、重複なしで1〜6個指定します。",
                        "minItems": 1,
                        "maxItems": MAX_APIS_PER_CALL,
                        "uniqueItems": True,
                    }
                )
                items = target_apis.get("items")
                if isinstance(items, dict):
                    items.update({"type": "integer", "minimum": 1, "maximum": 30})
            distance = properties.get("distance")
            year = properties.get("year")
            quarter = properties.get("quarter")
            division = properties.get("division")
            price_classification = properties.get("price_classification")
            language = properties.get("language")
            if isinstance(distance, dict):
                distance.update({"minimum": 0, "maximum": 425})
            if isinstance(year, dict):
                year.update({"type": "integer", "minimum": 1995})
            if isinstance(quarter, dict):
                quarter.update({"type": "integer", "minimum": 1, "maximum": 4})
            if isinstance(division, dict):
                division.update({"type": "array", "items": {"type": "string"}})
            if isinstance(price_classification, dict):
                price_classification.update({"enum": ["01", "02"]})
            if isinstance(language, dict):
                language.update({"enum": ["ja", "en"]})
        tool.description = (
            "指定した緯度・経度について、不動産情報ライブラリの公開データを取得します。"
            "target_apisには1〜30のAPI番号を1〜6個指定してください。主な番号は、"
            "1=不動産価格、3=地価、4=都市計画区域、5=用途地域、9=学校、"
            "11=医療機関、13=将来人口、16=災害危険区域、26=洪水、"
            "28=津波、29=土砂災害です。結果はGeoJSONと公式地図URLです。"
            "このリモート版は読み取り専用で、サーバーへファイルを保存しません。"
        )
    return tools


async def handle_list_tools() -> list[types.Tool]:
    """List the tools exposed by this server."""
    return _remote_tools()


async def handle_call_tool(name: str, arguments: dict[str, Any]) -> types.CallToolResult:
    """Validate a tool request and call the upstream MLIT APIs."""
    request_id = uuid.uuid4().hex
    logger.info("Tool called: %s (request_id: %s)", name, request_id)

    if name not in API_SPECS:
        return _error_result("存在しないツールです。")
    if not LIBRARY_API_KEY:
        return _error_result("不動産情報ライブラリAPIキーが設定されていません。")

    try:
        normalized = _normalize_arguments(arguments)
        payload = build_payload(spec=API_SPECS[name], args=normalized)
        result = await handle_request(payload)
    except (TypeError, ValueError) as error:
        return _error_result(str(error))
    except Exception:
        logger.exception("Tool execution failed (request_id: %s)", request_id)
        return _error_result("不動産情報ライブラリの取得処理に失敗しました。")

    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2),
            )
        ],
        structuredContent=result,
    )


def _normalize_arguments(arguments: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the public input boundary and disable container file writes."""
    if not isinstance(arguments, Mapping):
        raise TypeError("引数はオブジェクトで指定してください。")
    if "save_file" in arguments or "output_dir" in arguments:
        raise ValueError("リモート版ではファイル保存を利用できません。")

    normalized = dict(arguments)
    lat = normalized.get("lat")
    lon = normalized.get("lon")
    if isinstance(lat, bool) or not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        raise ValueError("latは-90〜90の数値で指定してください。")
    if isinstance(lon, bool) or not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        raise ValueError("lonは-180〜180の数値で指定してください。")

    target_apis = normalized.get("target_apis")
    if not isinstance(target_apis, list) or not 1 <= len(target_apis) <= MAX_APIS_PER_CALL:
        raise ValueError(f"target_apisは1〜{MAX_APIS_PER_CALL}個指定してください。")
    if any(isinstance(code, bool) or not isinstance(code, int) or not 1 <= code <= 30 for code in target_apis):
        raise ValueError("target_apisには1〜30の整数を指定してください。")
    if len(set(target_apis)) != len(target_apis):
        raise ValueError("target_apisに同じ番号を重複して指定できません。")

    distance = normalized.get("distance")
    if distance is not None and (
        isinstance(distance, bool)
        or not isinstance(distance, (int, float))
        or not 0 <= distance <= 425
    ):
        raise ValueError("distanceは0〜425メートルの数値で指定してください。")

    normalized["save_file"] = False
    normalized.pop("output_dir", None)
    return normalized


def _error_result(message: str) -> types.CallToolResult:
    data = {"status": "error", "data": message}
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=json.dumps(data, ensure_ascii=False),
            )
        ],
        structuredContent=data,
        isError=True,
    )


async def _on_list_tools(_context: Any, _params: Any) -> types.ListToolsResult:
    return types.ListToolsResult(tools=await handle_list_tools())


async def _on_call_tool(
    _context: Any,
    params: types.CallToolRequestParams,
) -> types.CallToolResult:
    return await handle_call_tool(params.name, params.arguments or {})


server = Server(
    SERVER_NAME,
    version=SERVER_VERSION,
    description="不動産情報ライブラリの地理空間データを座標から検索する読み取り専用MCPサーバー",
    on_list_tools=_on_list_tools,
    on_call_tool=_on_call_tool,
)


async def health(_: Request) -> JSONResponse:
    """Container health endpoint. The edge Worker protects this path."""
    return JSONResponse({"status": "ok", "version": SERVER_VERSION})


def create_http_app():
    """Create the stateless Streamable HTTP application."""
    return server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        host="0.0.0.0",
        custom_starlette_routes=[Route("/health", health, methods=["GET"])],
    )


async def _run_stdio() -> None:
    async with stdio_server() as (read, write):
        options = server.create_initialization_options(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        )
        await server.run(read, write, options)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport == "streamable-http":
        uvicorn.run(
            create_http_app(),
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8080")),
            log_level=os.getenv("LOG_LEVEL", "warning").lower(),
        )
        return
    if transport != "stdio":
        raise ValueError(f"未対応のMCP_TRANSPORTです: {transport}")
    anyio.run(_run_stdio)


if __name__ == "__main__":
    main()
