import requests

from utils.const import RGEOCODER_URL

# 接続5秒・読み取り30秒。MCPサーバー全体のハングを防ぐ。
DEFAULT_TIMEOUT = (5, 30)


# 住所から緯度経度(国土地理院のジオコーダ)
def get_latlon(full_addr):
    response = requests.get(
        f"{RGEOCODER_URL}?q={full_addr}",
        headers={"User-Agent": "REINS-Client"},
        timeout=DEFAULT_TIMEOUT,
    )

    result = response.json()

    if result and isinstance(result, list) and len(result) > 0:
        lon = result[0]["geometry"]["coordinates"][0]
        lat = result[0]["geometry"]["coordinates"][1]
        coordinates = [lon, lat]
        return coordinates
    else:
        return [None, None]
