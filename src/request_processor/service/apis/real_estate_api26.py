from request_processor.service.apis.base_api import BasePolygonApi
from utils.const import LIBRARY_API_URL


class RealEstateApi26(BasePolygonApi):
    API_CONFIG = {
        "name": "国土数値情報（洪水浸水想定区域（想定最大規模））",
        "path": f"{LIBRARY_API_URL}/XKT026",
        "response_type": "geojson",
    }
