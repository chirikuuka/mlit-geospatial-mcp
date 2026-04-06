import logging

from request_processor.service.apis.base_api import BasePointApi
from utils.const import LIBRARY_API_URL

logger = logging.getLogger(__name__)


class RealEstateApi12(BasePointApi):
    API_CONFIG = {
        "name": "国土数値情報（福祉施設）",
        "path": f"{LIBRARY_API_URL}/XKT011",
        "response_type": "geojson",
    }

    def _build_params(self, x, y):
        params = super()._build_params(x, y)
        optional_param_mapping = {
            "administrativeAreaCode": "administrative_area_code",
            "welfareFacilityClassCode": "welfare_facility_class_code",
            "welfareFacilityMiddleClassCode": "welfare_facility_middle_class_code",
            "welfareFacilityMinorClassCode": "welfare_facility_minor_class_code",
        }
        for api_key, req_key in optional_param_mapping.items():
            value = self.req_body.get(req_key)
            if value is not None:
                params[api_key] = (
                    ",".join(map(str, value)) if isinstance(value, list) else value
                )
        return params
