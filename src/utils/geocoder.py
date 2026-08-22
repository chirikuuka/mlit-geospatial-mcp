import requests

from utils.const import RGEOCODER_URL


def get_latlon(full_addr):
    """住所を国土地理院APIで緯度経度へ変換する。"""
    response = requests.get(
        RGEOCODER_URL,
        params={"q": full_addr},
        headers={"User-Agent": "REINS-Client"},
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if result and isinstance(result, list):
        lon = result[0]["geometry"]["coordinates"][0]
        lat = result[0]["geometry"]["coordinates"][1]
        return [lon, lat]
    return [None, None]
