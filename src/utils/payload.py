import logging

from utils.definitions import ApiSpec

logger = logging.getLogger(__name__)


def build_payload(
    *,
    spec: ApiSpec,
    args: dict,
) -> dict:
    """
    引数を内部処理用のpayloadを生成。

    Args:
        spec(ApiSpec): 対象APIの定義
        args(dict):toolからの引数

    Returns:
        payload(dict): 内部処理用に整形したpayload
            - coordinates: 緯度・経度の配列
            - target_apis: 対象APIのリスト
            - 任意のパラメータ: 各APIの指定可能なパラメータ
    """

    payload = {
        "coordinates": [
            {
                "lat": float(args["lat"]),
                "lon": float(args["lon"]),
            }
        ],
    }

    payload["target_apis"] = args.get("target_apis", [])

    # 任意パラメータを許可リストベースで追加
    for param in spec.allowed_params:
        if param in args and args[param] is not None:
            payload[param] = args[param]

    logger.info(f"build payload:{payload}")

    return payload
