import requests

from utils.const import RE_RGEOCODER_URL


def get_citycd(lat, lon):
    """緯度経度を国土地理院APIで市区町村コードへ変換する。"""
    response = requests.get(
        RE_RGEOCODER_URL,
        params={"lat": lat, "lon": lon},
        headers={"User-Agent": "REINS-Client"},
        timeout=20,
    )
    if response.status_code != 200:
        return None, None

    result = response.json()
    return result["results"]["muniCd"], result["results"]["lv01Nm"]
