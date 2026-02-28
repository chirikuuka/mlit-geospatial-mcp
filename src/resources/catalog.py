import json
from typing import Any

import mcp.types as types

from tools import TOOLS

SERVER_NAME = "mlit-geospatial-mcp"

TOOLS_RESOURCE_URI = f"resource://{SERVER_NAME}/tools"
RESOURCES_RESOURCE_URI = f"resource://{SERVER_NAME}/resources"
PROMPTS_RESOURCE_URI = f"resource://{SERVER_NAME}/prompts"
CATALOG_RESOURCE_URI = f"resource://{SERVER_NAME}/catalog"
OVERVIEW_RESOURCE_URI = f"resource://{SERVER_NAME}/overview"

PROMPTS: list[types.Prompt] = [
    types.Prompt(
        name="server_usage_guide",
        title="Server Usage Guide",
        description="このサーバーの主要な tool / resource の使い分けを案内します。",
    )
]


def _dump_model(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return {
            key: item for key, item in vars(value).items() if not key.startswith("_")
        }
    return str(value)


def _summarize_tool(tool: types.Tool) -> dict[str, Any]:
    schema = tool.inputSchema or {}
    properties = schema.get("properties", {})
    return {
        "name": tool.name,
        "title": tool.title,
        "description": tool.description,
        "required": schema.get("required", []),
        "optional": sorted(
            name for name in properties.keys() if name not in schema.get("required", [])
        ),
    }


def _summarize_resource(resource: types.Resource) -> dict[str, Any]:
    return {
        "name": resource.name,
        "title": resource.title,
        "uri": str(resource.uri),
        "description": resource.description,
        "mimeType": resource.mimeType,
    }


def _summarize_prompt(prompt: types.Prompt) -> dict[str, Any]:
    return {
        "name": prompt.name,
        "title": prompt.title,
        "description": prompt.description,
        "arguments": [_dump_model(argument) for argument in prompt.arguments or []],
    }


def _tools_payload() -> dict[str, Any]:
    return {
        "server": SERVER_NAME,
        "count": len(TOOLS),
        "summary": [_summarize_tool(tool) for tool in TOOLS],
        "items": [_dump_model(tool) for tool in TOOLS],
    }


def _resources_payload() -> dict[str, Any]:
    return {
        "server": SERVER_NAME,
        "count": len(RESOURCES),
        "summary": [_summarize_resource(resource) for resource in RESOURCES],
        "items": [_dump_model(resource) for resource in RESOURCES],
    }


def _prompts_payload() -> dict[str, Any]:
    return {
        "server": SERVER_NAME,
        "count": len(PROMPTS),
        "summary": [_summarize_prompt(prompt) for prompt in PROMPTS],
        "items": [_dump_model(prompt) for prompt in PROMPTS],
    }


def _overview_payload() -> dict[str, Any]:
    return {
        "server": SERVER_NAME,
        "purpose": "不動産情報ライブラリと周辺GIS情報をMCP toolとして提供するサーバーです。",
        "recommended_entrypoints": [
            {
                "tool": "get_multi_api",
                "when": "複数APIをまとめて引きたいとき",
            },
            {
                "tool": "get_land_price_point_by_location",
                "when": "地価公示・地価調査ポイントだけを探したいとき",
            },
            {
                "tool": "plateau_space_id",
                "when": "PLATEAU連携の前に空間IDが必要なとき",
            },
        ],
        "resources": [
            {
                "uri": TOOLS_RESOURCE_URI,
                "purpose": "tool の完全定義",
            },
            {
                "uri": CATALOG_RESOURCE_URI,
                "purpose": "tools / resources / prompts の完全カタログ",
            },
            {
                "uri": OVERVIEW_RESOURCE_URI,
                "purpose": "短い利用案内",
            },
        ],
    }


RESOURCE_BODIES = {
    TOOLS_RESOURCE_URI: _tools_payload,
    RESOURCES_RESOURCE_URI: _resources_payload,
    PROMPTS_RESOURCE_URI: _prompts_payload,
    OVERVIEW_RESOURCE_URI: _overview_payload,
    CATALOG_RESOURCE_URI: lambda: {
        "server": SERVER_NAME,
        "overview": _overview_payload(),
        "tools": _tools_payload(),
        "resources": _resources_payload(),
        "prompts": _prompts_payload(),
    },
}


RESOURCES = [
    types.Resource(
        uri=TOOLS_RESOURCE_URI,
        name="tools",
        title="Server Tools",
        description="このMCPサーバーが提供するtools一覧です。",
        mimeType="application/json",
    ),
    types.Resource(
        uri=RESOURCES_RESOURCE_URI,
        name="resources",
        title="Server Resources",
        description="このMCPサーバーが提供するresources一覧です。",
        mimeType="application/json",
    ),
    types.Resource(
        uri=PROMPTS_RESOURCE_URI,
        name="prompts",
        title="Server Prompts",
        description="このMCPサーバーが提供するprompts一覧です。",
        mimeType="application/json",
    ),
    types.Resource(
        uri=OVERVIEW_RESOURCE_URI,
        name="overview",
        title="Server Overview",
        description="このMCPサーバーの短い利用案内です。",
        mimeType="application/json",
    ),
    types.Resource(
        uri=CATALOG_RESOURCE_URI,
        name="catalog",
        title="Server Catalog",
        description="tools / resources / prompts をまとめたサーバーカタログです。",
        mimeType="application/json",
    ),
]


def build_resource_contents(uri: str) -> list[types.TextResourceContents]:
    if uri not in RESOURCE_BODIES:
        raise ValueError(f"Unknown resource URI: {uri}")

    body = RESOURCE_BODIES[uri]()
    return [
        types.TextResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(body, ensure_ascii=False, indent=2),
        )
    ]


def build_prompt(name: str, arguments: dict[str, Any] | None = None) -> types.GetPromptResult:
    # Prompt引数は将来拡張用に受け取るが、現状の server_usage_guide では未使用。
    _ = arguments

    if name != "server_usage_guide":
        raise ValueError(f"Unknown prompt name: {name}")

    detail = json.dumps(_overview_payload(), ensure_ascii=False, indent=2)
    return types.GetPromptResult(
        description="このサーバーの使い分けを説明するプロンプトです。",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=(
                        "このサーバーを使う前提で、利用可能な tools / resources / prompts の概要を説明し、"
                        "どのケースでどの tool を選ぶべきか案内してください。\n\n"
                        f"{detail}"
                    ),
                ),
            )
        ],
    )
