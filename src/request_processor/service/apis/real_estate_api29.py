from request_processor.common.point_filter import filter_distance
from request_processor.common.polygon_filter import overlap_judge
from request_processor.service.apis.base_api import BasePointApi
from utils.const import LIBRARY_API_URL


class RealEstateApi29(BasePointApi):
    API_CONFIG = {
        "name": "国土数値情報（土砂災害警戒区域）",
        "path": f"{LIBRARY_API_URL}/XKT029",
        "response_type": "geojson",
    }

    def _process_data(self, data):
        if not data or not data.get("features"):
            self.logger.info(f"{self.API_CONFIG.get('name', '')}の該当データなし")
            return None

        latlon = (self.converted["lat"], self.converted["lon"])
        distance = self.req_body.get("distance")
        filtered_features = []
        for feature in data["features"]:
            geom_type = feature.get("geometry", {}).get("type")
            if geom_type in ("Polygon", "MultiPolygon"):
                if overlap_judge([feature], latlon):
                    filtered_features.append(feature)
            elif geom_type == "LineString":
                if filter_distance([feature], latlon, distance):
                    filtered_features.append(feature)
        if not filtered_features:
            self.logger.info(
                f"{self.API_CONFIG.get('name', '')}の該当データなし（絞り込み後）"
            )
            return None

        data["features"] = filtered_features
        return data
