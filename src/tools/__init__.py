"""
MCPツールの初期化モジュール。

このモジュールでは、各ツールのAPI仕様とツール定義をインポートし、
MCPに登録するためのリストと辞書を提供。

Attributes:
    TOOLS (list): MCPに登録するツールのリスト。
    API_SPECS (dict): ツール名をキーとしたAPI仕様の辞書。
"""

from tools.multi_api import API_SPEC as MULTI_API_SPEC
from tools.multi_api import TOOL as MULTI_API_TOOL

# MCPに登録するツール一覧
TOOLS = [
    MULTI_API_TOOL,
]

# tool_name→ApiSpecの辞書
API_SPECS = {
    MULTI_API_SPEC.tool_name: MULTI_API_SPEC,
}
