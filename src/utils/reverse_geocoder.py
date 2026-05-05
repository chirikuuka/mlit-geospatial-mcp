import requests

from utils.const import RE_RGEOCODER_URL

# 接続5秒・読み取り30秒。MCPサーバー全体のハングを防ぐ。
DEFAULT_TIMEOUT = (5, 30)


# 緯度経度から都道府県CD検索(国土地理院による逆ジオコーダ)
def get_citycd(lat, lon):
    response = requests.get(
        f"{RE_RGEOCODER_URL}?lat={lat}&lon={lon}",
        headers={"User-Agent": "REINS-Client"},
        timeout=DEFAULT_TIMEOUT,
    )
    if response.status_code == 200:
        result = response.json()
        # 都道府県コード
        muni_cd = result["results"]["muniCd"]
        # 市区町村名
        lv_01_nm = result["results"]["lv01Nm"]

        return muni_cd, lv_01_nm

    else:
        return None, None
