"""
地理空間サービスモジュール。

このモジュールは、座標変換や複数APIの並列呼び出しを行うサービスクラスを提供。

Classes:
    GeospatialService:
        内部ツールの中核処理を担当するクラス
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from request_processor.enums.api_enum import APIEnum
from request_processor.models.api_models import RequestModel
from utils.const import ZOOM
from utils.coordinates_conversion import (
    latlon_to_address,
    latlon_to_tile_fraction,
)
from utils.logger_config import setup_logger
from utils.map_url_generator import build_map_url


class GeospatialService:
    # 内部ツールの中核処理
    def __init__(self):
        self.logger = setup_logger(__name__)

    def converted_coordinate(self, coord):
        """
        座標をタイル座標や住所情報に変換。

        Args:
            coord: 緯度・経度を含むオブジェクト

        Returns:
            dict[str, float]: 変換後の座標情報
        """
        x, y, x_frac, y_frac = latlon_to_tile_fraction(coord.lat, coord.lon, ZOOM)
        muni_cd, lv_01_nm = latlon_to_address(coord.lat, coord.lon)

        converted = {
            "lat": coord.lat,
            "lon": coord.lon,
            "x": x,
            "y": y,
            "x_frac": x_frac,
            "y_frac": y_frac,
            "muni_cd": muni_cd,
            "lv_01_nm": lv_01_nm,
        }
        return converted

    async def process_request(self, req: RequestModel):
        """
        リクエストを処理し、複数APIを並列で呼び出す。

        Args:
            req (RequestModel): 内部処理用にRequestModelに合わせて整形したpayload

        Returns:
            dict[str, object]: 入力座標とAPI結果を含む辞書、不動産ライブラリの地図URLも含む
        """

        # save_fileが未指定(None)またはnullの場合は保存確認を促すレスポンスを返す
        save_file_value = getattr(req, "save_file", None)
        if save_file_value is None:
            return {
                "status": "need_confirmation",
                "message": (
                    "【重要】取得結果のファイルを保存しますか？ "
                    "save_file=true/false を必ずユーザーに選択させてください。"
                    "自動でfalseにしないでください。"
                ),
            }
        # null（JSONからのNone相当）も明示的に判定
        if str(save_file_value).lower() == "null":
            return {
                "status": "need_confirmation",
                "message": (
                    "【重要】取得結果のファイルを保存しますか？ "
                    "保存するかしないかを（save_file=true/false） を必ずユーザーに選択させてください。"
                    "自動でfalseにしないでください。"
                ),
            }

        base_output_folder = "C:/output"
        file_paths = []

        now_folder = datetime.now().strftime("%Y%m%d%H%M")

        for c in req.coordinates:
            # 座標から変換処理
            converted = self.converted_coordinate(c)

            # リクエストのモデルをdictに変換
            req_dict = req.model_dump()

            # APIごとのインスタンス化
            apis = []
            for code in req.target_apis:
                api_enum = APIEnum.from_code(code)
                instance = api_enum.get_instance(
                    req_dict,
                    converted,
                )
                apis.append(instance)

            # exchange()を非同期で並列実行
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(None, api.exchange) for api in apis]
            api_results = await asyncio.gather(*tasks)

            # build_map_urlで地図URL生成
            map_url = build_map_url(c.lat, c.lon, req.target_apis, req_dict)

            # save_fileがTrueならファイル保存
            file_paths = []
            if hasattr(req, "save_file") and req.save_file:
                # 保存対象を一時的に集める
                save_targets = []
                for idx, result in enumerate(api_results):
                    # 完全な None をスキップ
                    if result is None:
                        continue

                    payload_to_write = result
                    file_name = None

                    if isinstance(result, dict):
                        # file_name の取得
                        if (
                            "file_name" in result
                            and isinstance(result["file_name"], str)
                            and result["file_name"].strip()
                        ):
                            file_name = result["file_name"].strip()

                        # data を抽出
                        if "data" in result:
                            data = result.get("data")

                            # data が None/空ならスキップ
                            if data is None:
                                continue

                            # data が dict/list で空ならスキップ
                            if isinstance(data, (dict, list)) and not data:
                                continue

                            # GeoJSON 想定: features が空のときはスキップ
                            if isinstance(data, dict):
                                features = data.get("features", None)
                                if isinstance(features, list) and len(features) == 0:
                                    continue

                            payload_to_write = data

                    # 保存対象が決まったらリストに追加
                    save_targets.append((idx, payload_to_write, file_name))

                # 保存対象が1つ以上ある場合のみフォルダ作成・保存
                if save_targets:
                    output_dir = getattr(req, "output_dir", None)
                    if (
                        output_dir
                        and isinstance(output_dir, str)
                        and output_dir.strip()
                    ):
                        output_folder = Path(output_dir.strip()) / now_folder
                    else:
                        output_folder = Path(base_output_folder) / now_folder
                    output_folder.mkdir(parents=True, exist_ok=True)

                    for idx, payload_to_write, file_name in save_targets:
                        if not file_name:
                            file_name = f"api_result_{idx + 1}.geojson"

                        file_path = output_folder / file_name
                        try:
                            with open(file_path, "w", encoding="utf-8") as f:
                                if isinstance(payload_to_write, (dict, list)):
                                    json.dump(
                                        payload_to_write,
                                        f,
                                        ensure_ascii=False,
                                        indent=2,
                                    )
                                else:
                                    f.write(str(payload_to_write))
                            file_paths.append(str(file_path))
                        except Exception as e:
                            self.logger.error(f"ファイル保存失敗: {file_path} - {e}")
                            file_paths.append(None)

        return {
            "input": {"lat": c.lat, "lon": c.lon},
            "api_results": api_results,
            "map_url": map_url,
            "saved_file_paths": file_paths,
        }
