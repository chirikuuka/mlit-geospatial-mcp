"""
地図表示URL生成ロジック
lat, lon, target_apis から地図表示用URLを生成する
"""

from utils.const import MAP_URL_ZOOM, SURVER_YEAR

# target_api番号 → レイヤ・条件・追加パラメータ対応表
API_LAYERS = {
    3: [
        {
            "layer": "publicNotices",
            "condition": lambda p: (
                p.get("land_price_classification") in (None, "0")
                and (
                    not p.get("use_category_code")
                    or any(
                        code.strip() in LAYER_PARAMS["publicNotices"]
                        for code in p.get("use_category_code", [])
                        if code.strip()
                    )
                )
            ),
            "params": lambda p: (
                [
                    f"publicNotices={c.strip()}"
                    for c in p.get("use_category_code", [])
                    if c.strip()
                ]
                if p.get("use_category_code")
                else [f"publicNotices={v}" for v in LAYER_PARAMS["publicNotices"]]
            ),
        },
        {
            "layer": "surveys",
            "condition": lambda p: (
                p.get("land_price_classification") in (None, "1")
                and (
                    not p.get("use_category_code")
                    or any(
                        code.strip() in LAYER_PARAMS["publicNotices"]
                        for code in p.get("use_category_code", [])
                        if code.strip()
                    )
                )
            ),
            "params": lambda p: (
                [
                    f"publicNotices={c.strip()}"
                    for c in p.get("use_category_code", [])
                    if c.strip()
                ]
                if p.get("use_category_code")
                else [f"publicNotices={v}" for v in LAYER_PARAMS["publicNotices"]]
            ),
        },
    ],
    12: [
        {
            "layer": "welfareFacility",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
        # 分類レイヤー
        *[
            {
                "layer": l,
                "condition": lambda p, l=l, code=code: (
                    isinstance(p.get("welfare_facility_class_code"), list)
                    and any(
                        (c and isinstance(c, str) and c.strip() == code)
                        for c in p.get("welfare_facility_class_code")
                    )
                ),
                "params": lambda p: [],
            }
            for l, code in [
                ("shelterLayer", "01"),
                ("elderlyWelfareFacilityLayer", "02"),
                ("facilityForTheHandicappedLayer", "03"),
                ("socialParticipationSupportFacilitiesLayer", "04"),
                ("childWelfareFacilityLayer", "05"),
                ("maternalAndChildWelfareLayer", "06"),
                ("otherWelfareFacilityLayer", "99"),
            ]
        ],
        # 指定がなければ全分類レイヤー
        *[
            {
                "layer": l,
                "condition": lambda p: (
                    not (
                        isinstance(p.get("welfare_facility_class_code"), list)
                        and p.get("welfare_facility_class_code")
                    )
                ),
                "params": lambda p: [],
            }
            for l in [
                "shelterLayer",
                "elderlyWelfareFacilityLayer",
                "facilityForTheHandicappedLayer",
                "socialParticipationSupportFacilitiesLayer",
                "childWelfareFacilityLayer",
                "maternalAndChildWelfareLayer",
                "otherWelfareFacilityLayer",
            ]
        ],
    ],
    # 他APIは従来通りレイヤ名のみ
    4: [
        {"layer": l, "condition": lambda p, l=l: True, "params": lambda p: []}
        for l in [
            "urbanPlanAreaLayer",
            "areaClassification",
            "urbanizationPromotionAreaLayer",
            "urbanizationControlAreaLayer",
        ]
    ],
    5: [
        {
            "layer": "useAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    6: [
        {
            "layer": "locationOptimizePlanAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    7: [
        {
            "layer": "elementarySchoolAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    8: [
        {
            "layer": "juniorHighSchoolAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    9: [
        {"layer": l, "condition": lambda p, l=l: True, "params": lambda p: []}
        for l in [
            "school",
            "elementarySchoolLayer",
            "juniorHighSchoolLayer",
            "secondarySchoolLayer",
            "highSchoolLayer",
            "technicalSchoolLayer",
            "juniorCollegeLayer",
            "universityLayer",
            "specialSupportSchoolLayer",
            "compulsoryEducationSchoolLayer",
            "miscellaneousSchoolLayer",
            "professionalTrainingCollegeLayer",
        ]
    ],
    10: [
        {
            "layer": "preschoolLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    11: [
        {"layer": l, "condition": lambda p, l=l: True, "params": lambda p: []}
        for l in [
            "medicalInstitution",
            "hospitalLayer",
            "clinicLayer",
            "dentalClinicLayer",
        ]
    ],
    14: [
        {
            "layer": "fireProtectionAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    15: [
        {
            "layer": "passengersByStationLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    16: [
        {
            "layer": "disasterRiskAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    17: [
        {
            "layer": "culturalFacilityLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    18: [
        {"layer": l, "condition": lambda p, l=l: True, "params": lambda p: []}
        for l in [
            "cityTownHall",
            "townHallLayer",
            "townHallBranchLayer",
            "otherAdministrativeServicesLayer",
            "publicHallLayer",
            "meetingFacilityLayer",
        ]
    ],
    19: [
        {
            "layer": "naturalParkAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    20: [
        {
            "layer": "developedLandLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    21: [
        {
            "layer": "landslidePreventionLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    22: [
        {
            "layer": "collapseRiskAreaLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    23: [
        {
            "layer": "districtPlanLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    24: [
        {
            "layer": "advancedUseLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    25: [
        {
            "layer": "liqueFactionLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    26: [
        {
            "layer": "shinsuishin-layer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    27: [
        {
            "layer": "hightideShinsuishinLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    28: [
        {
            "layer": "tsunamiLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
    29: [
        {"layer": l, "condition": lambda p, l=l: True, "params": lambda p: []}
        for l in [
            "sedimentDisasterArea",
            "dosekiryukeikaikuikiLayer",
            "kyukeishakeikaikuikiLayer",
            "jisuberikeikaikuikiLayer",
        ]
    ],
    30: [
        {
            "layer": "denselyInhabitedDistrictLayer",
            "condition": lambda p: True,
            "params": lambda p: [],
        },
    ],
}

# レイヤ個別パラメータ（例：地価公示の用途区分）
LAYER_PARAMS = {
    "publicNotices": ["00", "03", "05", "07", "09", "10", "13", "20"],
}


# --- 地図表示URL生成 ---
def build_map_url(
    lat: float, lon: float, target_apis: list[int], params: dict = None
) -> str:
    """
    地図表示URLを生成する（API_LAYERSの条件・パラメータ対応で分岐レス）

    1. API3ならsurveyYearを追加
    2. API_LAYERSの各レイヤ条件関数でTrueになったものだけ追加
    3. 追加パラメータ関数で返された値もURLに追加
    4. 座標・ズーム値（API3かつyear指定ならyear、なければデフォルト）を追加
    5. すべてのパラメータを&区切りでURLにして返す
    """
    base_url = "https://www.reinfolib.mlit.go.jp/map?"
    url_params: list[str] = []
    params = params or {}

    # API 3: surveyYearはparams["year"]があればそれを、なければSURVER_YEAR
    if 3 in target_apis:
        year = params.get("year")
        if isinstance(year, int) or (isinstance(year, float) and year.is_integer()):
            url_params.append(f"surveyYear={int(year)}")
        else:
            url_params.append(f"surveyYear={SURVER_YEAR}")

    for api in target_apis:
        for entry in API_LAYERS.get(api, []):
            if entry["condition"](params):
                url_params.append(f"layers={entry['layer']}")
                for v in entry["params"](params):
                    url_params.append(v)

    # 座標・ズーム（zoomは常にMAP_URL_ZOOM固定）
    url_params.append(f"x={lat}")
    url_params.append(f"y={lon}")
    url_params.append(f"zoom={MAP_URL_ZOOM}")

    return base_url + "&".join(url_params)
