from datetime import datetime
from typing import ClassVar, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator


# リクエストモデル
class coodinatesItem(BaseModel):
    lat: float
    lon: float


class RequestModel(BaseModel):
    coordinates: List[coodinatesItem]
    target_apis: Optional[List[int]] = None
    distance: Optional[int] = 425
    landmap_distance: Optional[int] = 50
    price_classification: Optional[str] = None
    year: Optional[int] = datetime.now().year - 1
    quarter: Optional[int] = None
    language: Optional[str] = None
    division: Optional[List[str]] = ["00", "03", "05", "07", "09", "10", "13", "20"]
    land_price_classification: Optional[str] = None
    use_category_code: Optional[List[str]] = None
    administrative_area_code: Optional[List[str]] = None
    welfare_facility_class_code: Optional[List[str]] = None
    welfare_facility_middle_class_code: Optional[List[str]] = None
    welfare_facility_minor_class_code: Optional[List[str]] = None
    prefecture_code: Optional[List[str]] = None
    district_code: Optional[List[str]] = None
    save_file: Optional[bool] = None
    output_dir: Optional[str] = None

    # 任意設定
    conditional_fields: ClassVar[Dict[str, List[int]]] = {
        "distance": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
        ],
        "price_classification": [1],
        "year": [1, 2, 3],
        "quarter": [1],
        "language": [1],
        "division": [2],
        "land_price_classification": [3],
        "use_category_code": [3],
        "administrative_area_code": [7, 8, 12, 16, 17, 21, 22, 30],
        "welfare_facility_class_code": [12],
        "welfare_facility_middle_class_code": [12],
        "welfare_facility_minor_class_code": [12],
        "prefecture_code": [19, 21, 22],
        "district_code": [19],
    }

    # target_apisが空なら全指定
    @field_validator("target_apis", mode="before")
    @classmethod
    def default_target_apis(cls, v):
        if not v:
            return [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
            ]
        return v

    # 必須チェック
    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Please specify one or more coordinates")
        return v

    @model_validator(mode="after")
    def validate_fields(self):
        target_apis_list = self.target_apis or []
        for field_name, required_values in RequestModel.conditional_fields.items():
            if hasattr(self, field_name):
                if not any(v in target_apis_list for v in required_values):
                    setattr(self, field_name, None)
        return self


# レスポンスモデル
class ResponseModel(BaseModel):
    status: str
    message: str
