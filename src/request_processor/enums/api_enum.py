from enum import IntEnum

from request_processor.service.apis.real_estate_api1 import RealEstateApi1
from request_processor.service.apis.real_estate_api2 import RealEstateApi2
from request_processor.service.apis.real_estate_api3 import RealEstateApi3
from request_processor.service.apis.real_estate_api4 import RealEstateApi4
from request_processor.service.apis.real_estate_api5 import RealEstateApi5
from request_processor.service.apis.real_estate_api6 import RealEstateApi6
from request_processor.service.apis.real_estate_api7 import RealEstateApi7
from request_processor.service.apis.real_estate_api8 import RealEstateApi8
from request_processor.service.apis.real_estate_api9 import RealEstateApi9
from request_processor.service.apis.real_estate_api10 import RealEstateApi10
from request_processor.service.apis.real_estate_api11 import RealEstateApi11
from request_processor.service.apis.real_estate_api12 import RealEstateApi12
from request_processor.service.apis.real_estate_api13 import RealEstateApi13
from request_processor.service.apis.real_estate_api14 import RealEstateApi14
from request_processor.service.apis.real_estate_api15 import RealEstateApi15
from request_processor.service.apis.real_estate_api16 import RealEstateApi16
from request_processor.service.apis.real_estate_api17 import RealEstateApi17
from request_processor.service.apis.real_estate_api18 import RealEstateApi18
from request_processor.service.apis.real_estate_api19 import RealEstateApi19
from request_processor.service.apis.real_estate_api20 import RealEstateApi20
from request_processor.service.apis.real_estate_api21 import RealEstateApi21
from request_processor.service.apis.real_estate_api22 import RealEstateApi22
from request_processor.service.apis.real_estate_api23 import RealEstateApi23
from request_processor.service.apis.real_estate_api24 import RealEstateApi24
from request_processor.service.apis.real_estate_api25 import RealEstateApi25
from request_processor.service.apis.real_estate_api26 import RealEstateApi26
from request_processor.service.apis.real_estate_api27 import RealEstateApi27
from request_processor.service.apis.real_estate_api28 import RealEstateApi28
from request_processor.service.apis.real_estate_api29 import RealEstateApi29
from request_processor.service.apis.real_estate_api30 import RealEstateApi30


class APIEnum(IntEnum):
    # APIコードとクラスを関連付けるEnum
    API1 = 1
    API2 = 2
    API3 = 3
    API4 = 4
    API5 = 5
    API6 = 6
    API7 = 7
    API8 = 8
    API9 = 9
    API10 = 10
    API11 = 11
    API12 = 12
    API13 = 13
    API14 = 14
    API15 = 15
    API16 = 16
    API17 = 17
    API18 = 18
    API19 = 19
    API20 = 20
    API21 = 21
    API22 = 22
    API23 = 23
    API24 = 24
    API25 = 25
    API26 = 26
    API27 = 27
    API28 = 28
    API29 = 29
    API30 = 30

    def get_instance(
        self,
        req_body: dict,
        converted: dict,
    ):
        # APIコードに対応するクラスをインスタンス化して返す
        cls = CLASS_MATRIX.get(self)
        if not cls:
            raise ValueError(f"存在しないAPIコード：{self}")

        return cls(req_body, converted)

    @classmethod
    def from_code(cls, code: int):
        # 数字のコードからEnumを取得
        try:
            return APIEnum(code)
        except ValueError:
            raise ValueError(f"存在しないAPIコード：{code}")


# マトリクス（コード→クラスの対応表）
CLASS_MATRIX = {
    APIEnum.API1: RealEstateApi1,
    APIEnum.API2: RealEstateApi2,
    APIEnum.API3: RealEstateApi3,
    APIEnum.API4: RealEstateApi4,
    APIEnum.API5: RealEstateApi5,
    APIEnum.API6: RealEstateApi6,
    APIEnum.API7: RealEstateApi7,
    APIEnum.API8: RealEstateApi8,
    APIEnum.API9: RealEstateApi9,
    APIEnum.API10: RealEstateApi10,
    APIEnum.API11: RealEstateApi11,
    APIEnum.API12: RealEstateApi12,
    APIEnum.API13: RealEstateApi13,
    APIEnum.API14: RealEstateApi14,
    APIEnum.API15: RealEstateApi15,
    APIEnum.API16: RealEstateApi16,
    APIEnum.API17: RealEstateApi17,
    APIEnum.API18: RealEstateApi18,
    APIEnum.API19: RealEstateApi19,
    APIEnum.API20: RealEstateApi20,
    APIEnum.API21: RealEstateApi21,
    APIEnum.API22: RealEstateApi22,
    APIEnum.API23: RealEstateApi23,
    APIEnum.API24: RealEstateApi24,
    APIEnum.API25: RealEstateApi25,
    APIEnum.API26: RealEstateApi26,
    APIEnum.API27: RealEstateApi27,
    APIEnum.API28: RealEstateApi28,
    APIEnum.API29: RealEstateApi29,
    APIEnum.API30: RealEstateApi30,
}
