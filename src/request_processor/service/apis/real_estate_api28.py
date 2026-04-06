from request_processor.service.apis.base_api import BasePolygonApi
from utils.const import LIBRARY_API_URL


class RealEstateApi28(BasePolygonApi):
    API_CONFIG = {
        "name": "国土数値情報（津波浸水想定）",
        "path": f"{LIBRARY_API_URL}/XKT028",
        "response_type": "geojson",
    }
