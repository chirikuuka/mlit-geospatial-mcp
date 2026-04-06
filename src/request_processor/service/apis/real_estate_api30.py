from request_processor.service.apis.base_api import BasePolygonApi
from utils.const import LIBRARY_API_URL


class RealEstateApi30(BasePolygonApi):
    API_CONFIG = {
        "name": "国土数値情報（人口集中地区）",
        "path": f"{LIBRARY_API_URL}/XKT031",
        "response_type": "geojson",
    }

    def _build_params(self):
        params = super()._build_params()
        # 任意のパラメータ
        optional_param_mapping = {
            "administrativeAreaCode": "administrative_area_code",
        }
        for api_key, req_key in optional_param_mapping.items():
            value = self.req_body.get(req_key)
            if value is not None:
                params[api_key] = (
                    ",".join(map(str, value)) if isinstance(value, list) else value
                )
        return params
