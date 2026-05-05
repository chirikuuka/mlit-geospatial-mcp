import requests

from utils.logger_config import setup_logger

# 外部API呼び出し共通処理

logger = setup_logger(__name__)

# 接続5秒・読み取り30秒。MCPサーバー全体のハングを防ぐ。
DEFAULT_TIMEOUT = (5, 30)


def get(
    url: str, params: dict = None, response_type: str = "json", headers: dict = None
):
    headers = headers or {"Accept": "*/*"}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()

        if response_type in ("json", "geojson"):
            return response.json()
        # elif response_type:

    except Exception as e:
        logger.error(f"API呼び出し失敗 URL:{url} params:{params} エラー:{e}")
        #     空配列で処理継続
        return {"data": []}
