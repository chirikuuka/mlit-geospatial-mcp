from request_processor.service.apis.base_api import BasePolygonApi
from utils.const import LIBRARY_API_URL


class RealEstateApi27(BasePolygonApi):
    API_CONFIG = {
        "name": "国土数値情報（高潮浸水想定区域）",
        "path": f"{LIBRARY_API_URL}/XKT027",
        "response_type": "geojson",
    }
