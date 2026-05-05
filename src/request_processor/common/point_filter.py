from typing import Dict, List, Tuple

from pyproj import Geod
from shapely import wkt
from shapely.ops import nearest_points

# WGS84 楕円体
GEOD = Geod(ellps="WGS84")


# 周辺タイルの座標を取得（中心含む）
def get_surrounding_tiles(x, y, x_frac, y_frac):
    if x_frac < 0.5 and y_frac < 0.5:
        tiles = [(x, y), (x - 1, y), (x - 1, y - 1), (x, y - 1)]
    elif x_frac >= 0.5 and y_frac < 0.5:
        tiles = [(x, y), (x + 1, y), (x + 1, y - 1), (x, y - 1)]
    elif x_frac >= 0.5 and y_frac >= 0.5:
        tiles = [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
    else:
        tiles = [(x, y), (x - 1, y), (x - 1, y + 1), (x, y + 1)]

    return tiles


def filter_distance(
    features: List[Dict], latlon: Tuple[float, float], distance: float
) -> List[Dict]:
    search_lat, search_lon = latlon
    search_geom = f"POINT({search_lon} {search_lat})"
    filtered = []

    for feature in features:
        # geojsonの座標情報
        geom = feature.get("geometry", {})
        geom_type = geom.get("type")
        coords = geom.get("coordinates")

        if geom_type == "Point":
            target_lon, target_lat = coords
            target_geom = f"POINT({target_lon} {target_lat})"
        elif geom_type == "LineString":
            coord_str = ", ".join(f"{lon} {lat}" for lon, lat in coords)
            target_geom = f"LINESTRING({coord_str})"
        else:
            # Point / LineString 以外（Polygon等）は距離フィルタ非対応のためスキップ
            continue

        # 距離チェック
        result = get_distance(search_geom, target_geom)

        if result <= distance:
            filtered.append(feature)

    return filtered


# 距離取得
def get_distance(geom1: str, geom2: str) -> float:
    g1 = wkt.loads(geom1)
    g2 = wkt.loads(geom2)
    # 平面で最近接点
    p1, p2 = nearest_points(g1, g2)
    # 楕円体（WGS84）距離
    _, _, dist_m = GEOD.inv(p1.x, p1.y, p2.x, p2.y)
    return dist_m
