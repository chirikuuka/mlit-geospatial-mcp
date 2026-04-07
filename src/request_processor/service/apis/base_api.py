from abc import ABC, abstractmethod

from request_processor.common import requester
from request_processor.common.point_filter import (
    filter_distance,
    get_surrounding_tiles,
)
from request_processor.common.polygon_filter import overlap_judge
from utils.const import LIBRARY_API_KEY, ZOOM
from utils.logger_config import setup_logger


class BaseApi(ABC):
    """
    すべてのAPI処理クラスの基底となる抽象クラス。
    """

    def __init__(self, req_body: dict, converted: dict, **kwargs):
        """
        コンストラクタ。リクエストボディ、変換済みデータ、ロガーを初期化する。
        """
        self.req_body = req_body
        self.converted = converted
        self.logger = setup_logger(self.__class__.__name__)

    @abstractmethod
    def exchange(self):
        """
        データ取得から加工までの一連の処理を実行する。
        サブクラスで必ず実装する。
        """
        pass


class BaseRealEstateApi(BaseApi):
    """
    不動産ライブラリのAPIを呼び出すクラスのための基底クラス。
    """

    API_CONFIG = {}

    @abstractmethod
    def _call_api(self):
        """APIを呼び出して生データを取得する。"""
        pass

    @abstractmethod
    def _process_data(self, data):
        """取得したデータを加工する。"""
        pass

    def exchange(self):
        self.logger.info(f"{self.API_CONFIG.get('name', '')} exchange 開始")
        try:
            raw_data = self._call_api()
            processed_data = self._process_data(raw_data)

            if processed_data is None:
                return None

            return {
                "file_name": f"{self.API_CONFIG.get('name', '')}.geojson",
                "data": processed_data,
            }
        except Exception as e:
            self.logger.error(f"{self.API_CONFIG.get('name', '')} exchange エラー:{e}")
            return None


class BasePointApi(BaseRealEstateApi):
    """
    周辺4タイル分の情報を取得し、距離で絞り込むAPIのための基底クラス。
    """

    def _call_api(self):
        tiles = get_surrounding_tiles(
            self.converted["x"],
            self.converted["y"],
            self.converted["x_frac"],
            self.converted["y_frac"],
        )
        merged_geojson = {"type": "FeatureCollection", "features": []}

        for x, y in tiles:
            self.logger.info(f"x:{x}, y:{y}")
            params = self._build_params(x, y)

            try:
                response = requester.get(
                    url=self.API_CONFIG["path"],
                    params=params,
                    response_type=self.API_CONFIG["response_type"],
                    headers={
                        "Ocp-Apim-Subscription-Key": f"{LIBRARY_API_KEY}",
                        "Accept": "*/*",
                    },
                )
                if response and isinstance(response, dict) and response.get("features"):
                    merged_geojson["features"].extend(response["features"])

            except Exception as e:
                self.logger.error(f"{self.API_CONFIG.get('name', '')} 呼び出し失敗:{e}")
                raise

        return merged_geojson

    def _build_params(self, x, y):
        """APIリクエストのパラメータを構築する。サブクラスでオーバーライド可能。"""
        return {"response_format": "geojson", "z": ZOOM, "x": x, "y": y}

    def _process_data(self, data):
        if not data or not data.get("features"):
            self.logger.info(f"{self.API_CONFIG.get('name', '')}の該当データなし")
            return None

        distance = self.req_body.get("distance")
        filtered_features = filter_distance(
            features=data["features"],
            latlon=(self.converted["lat"], self.converted["lon"]),
            distance=distance,
        )
        if not filtered_features:
            self.logger.info(
                f"{self.API_CONFIG.get('name', '')}の該当データなし（絞り込み後）"
            )
            return None

        data["features"] = filtered_features
        return data


class BasePolygonApi(BaseRealEstateApi):
    """
    ポリゴンデータを取得し、座標との重なりで絞り込むAPIのための基底クラス。
    """

    def _call_api(self):
        params = self._build_params()
        return requester.get(
            url=self.API_CONFIG["path"],
            params=params,
            response_type=self.API_CONFIG["response_type"],
            headers={
                "Ocp-Apim-Subscription-Key": f"{LIBRARY_API_KEY}",
                "Accept": "*/*",
            },
        )

    def _build_params(self):
        """APIリクエストのパラメータを構築する。"""
        return {
            "response_format": "geojson",
            "z": ZOOM,
            "x": self.converted["x"],
            "y": self.converted["y"],
        }

    def _process_data(self, data):
        if not data or not data.get("features"):
            self.logger.info(f"{self.API_CONFIG.get('name', '')}の該当データなし")
            return None

        filtered_features = overlap_judge(
            features=data["features"],
            latlon=(self.converted["lat"], self.converted["lon"]),
        )
        if not filtered_features:
            self.logger.info(
                f"{self.API_CONFIG.get('name', '')}の該当データなし（絞り込み後）"
            )
            return None

        data["features"] = filtered_features
        return data
