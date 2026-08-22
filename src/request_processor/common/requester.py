import requests

from utils.logger_config import setup_logger

logger = setup_logger(__name__)


def get(
    url: str,
    params: dict | None = None,
    response_type: str = "json",
    headers: dict | None = None,
):
    """Call an upstream API with TLS verification and a bounded timeout."""
    headers = headers or {"Accept": "*/*"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        if response_type in ("json", "geojson"):
            return response.json()
    except Exception as error:
        logger.error(
            "API呼び出し失敗 URL:%s エラー種別:%s",
            url,
            type(error).__name__,
        )
        return {"data": []}
