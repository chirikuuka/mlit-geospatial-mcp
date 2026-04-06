# APIの定義

from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class ApiSpec:
    """
    ツール名と許可されるパラメータ名の集合を保持するデータクラス

    Attributes:
        tool_name : tool名
        allowed_params: 指定可能なパラメータ
    """

    tool_name: str
    allowed_params: Set[str]
