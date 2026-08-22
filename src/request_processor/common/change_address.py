import re

import requests

from utils.const import LIBRARY_API_KEY, LIBRARY_API_URL

PREFECTURE_CODES = {
    "01": "北海道",
    "02": "青森県",
    "03": "岩手県",
    "04": "宮城県",
    "05": "秋田県",
    "06": "山形県",
    "07": "福島県",
    "08": "茨城県",
    "09": "栃木県",
    "10": "群馬県",
    "11": "埼玉県",
    "12": "千葉県",
    "13": "東京都",
    "14": "神奈川県",
    "15": "新潟県",
    "16": "富山県",
    "17": "石川県",
    "18": "福井県",
    "19": "山梨県",
    "20": "長野県",
    "21": "岐阜県",
    "22": "静岡県",
    "23": "愛知県",
    "24": "三重県",
    "25": "滋賀県",
    "26": "京都府",
    "27": "大阪府",
    "28": "兵庫県",
    "29": "奈良県",
    "30": "和歌山県",
    "31": "鳥取県",
    "32": "島根県",
    "33": "岡山県",
    "34": "広島県",
    "35": "山口県",
    "36": "徳島県",
    "37": "香川県",
    "38": "愛媛県",
    "39": "高知県",
    "40": "福岡県",
    "41": "佐賀県",
    "42": "長崎県",
    "43": "熊本県",
    "44": "大分県",
    "45": "宮崎県",
    "46": "鹿児島県",
    "47": "沖縄県",
}


def get_full_address(muni_cd: str, lv_01_nm: str) -> str:
    pref_name = get_pref_name(muni_cd)
    city_name = get_cityname(muni_cd)
    district_name = get_district_name(lv_01_nm)
    return f"{pref_name}{city_name}{district_name}"


# 都道府県名取得
def get_pref_name(muni_cd: str) -> str:
    pref_code = muni_cd[:2]
    pref_name = PREFECTURE_CODES.get(pref_code, "")
    return pref_name


# 市区町村名取得
def get_cityname(muni_cd: str) -> str:
    pref_cd = str(muni_cd)[:2]
    city_list = get_libraryapi(pref_cd)
    match = next((item for item in city_list["data"] if item["id"] == muni_cd), None)
    city_name = match["name"] if match else None
    return city_name


# 地名取得（大字）
def get_district_name(lv_01_nm: str) -> str:
    district_name = re.sub(r"([一二三四五六七八九十百千万]+|[0-9]+)丁目$", "", lv_01_nm)
    return district_name


# 不動産ライブラリAPI（都道府県）
def get_libraryapi(pref_cd):
    params = {"area": pref_cd}
    # API検索
    response = requests.get(
        f"{LIBRARY_API_URL}/{'XIT002'}",
        params=params,
        headers={
            "User-Agent": "REINS-Client",
            "Ocp-Apim-Subscription-Key": LIBRARY_API_KEY,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()
