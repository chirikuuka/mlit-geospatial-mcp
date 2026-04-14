"""
複数API同時処理ツール定義。

このモジュールは、複数の不動産関連APIを同時に呼び出すためのMCPツールを定義。

Attributes:
    API_SPEC (ApiSpec): ツールのAPI仕様
    TOOL (types.Tool): MCPツール定義
"""

from mcp import types

from utils.definitions import ApiSpec

API_SPEC = ApiSpec(
    tool_name="get_multi_api",
    allowed_params={
        "distance",
        "price_classification",
        "year",
        "quarter",
        "language",
        "division",
        "land_price_classification",
        "use_category_code",
        "administrative_area_code",
        "welfare_facility_class_code",
        "welfare_facility_middle_class_code",
        "welfare_facility_minors_class_code",
        "prefecture_code",
        "district_code",
        "save_file",
        "output_dir",
    },
)

TOOL = types.Tool(
    name=API_SPEC.tool_name,
    description="""
                    このtoolはtarget_apiに指定されたデータを取得します。
                    例：「地価公示と都市計画区域のデータが欲しい」の場合、こちらのtoolでtarget_api3,4が指定されます。

                    返却内容は、取得結果と不動産ライブラリの地図表示用URL（＋保存先ディレクトリ）です。

                    取得結果のgeojsonファイルを任意のフォルダに保存するかどうかユーザに必ず確認を行い、
                    保存する場合（save_file=true）は保存先フォルダをユーザに返却する。
                    ファイル保存に関してユーザが明示していない場合は、保存するか確認をしてほしいためNoneとしてください。
                    save_fileがNoneまたはnullの場合は、必ず「取得結果のファイルは保存しますか？」とユーザーに確認してください。
    
                【target_apis一覧】
                - 未指定：全API（空配列を指定）
                - 1:不動産価格（取引価格・成約価格）情報取得API
                - 2:鑑定評価書情報API
                - 3:地価公示・地価調査のポイント（点）API
                - 4:都市計画決定GISデータ（都市計画区域・区域区分）API
                - 5:都市計画決定GISデータ（用途地域）API
                - 6:都市計画決定GISデータ（立地適正化計画）API
                - 7:国土数値情報（小学校区）API
                - 8:国土数値情報（中学校区）API
                - 9:国土数値情報（学校）API
                - 10:国土数値情報（保育園・幼稚園等）API
                - 11:国土数値情報（医療機関）API
                - 12:国土数値情報（福祉施設）API
                - 13:国土数値情報（将来推計人口250mメッシュ）API
                - 14:都市計画決定GISデータ（防火・準防火地域）API
                - 15:国土数値情報（駅別乗降客数）API
                - 16:国土数値情報（災害危険区域）API
                - 17:国土数値情報（図書館）API
                - 18:国土数値情報（市区町村役場及び集会施設等）API
                - 19:国土数値情報（自然公園地域）API
                - 20:国土数値情報（大規模盛土造成地マップ）API
                - 21:国土数値情報（地すべり防止地区）API
                - 22:国土数値情報（急傾斜地崩壊危険区域）API
                - 23:都市計画決定GISデータ（地区計画）API
                - 24:都市計画決定GISデータ（高度利用地区）API
                - 25:国土交通省都市局（地形区分に基づく液状化の発生傾向図）API
                - 26:国土数値情報（洪水浸水想定区域（想定最大規模））API
                - 27:国土数値情報（高潮浸水想定区域）API
                - 28:国土数値情報（津波浸水想定）API
                - 29:国土数値情報（土砂災害警戒区域）API
                - 30:国土数値情報（人口集中地区）API
                
                【任意パラメータ】
                - distance：検索半径距離（API：1,2,3,9,10,11,12,15,17,18,29で指定可能）
                - price_classification：価格情報区分コード（API：1で指定可能）
                - year：対象年（API：1,2,3で指定可能）
                - quarter:取引時期（四半期）（API：1で指定可能）
                - language:出力結果の言語（API：1で指定可能）
                - division:用途区分（API：2で指定可能）
                - land_price_classification：地価情報区分コード（API：3で指定可能）
                - use_category_code：用途区分コード（API：3で指定可能）
                - administrative_area_code:行政区域コード（API：7,8,12,16,17,21,22,30で指定可能）
                - welfare_facility_class_code:福祉施設大分類コード（API：12で指定可能）
                - welfare_facility_middle_class_code:福祉施設中分類コード（API：12で指定可能）
                - welfare_facility_minor_class_code:福祉施設小分類コード（API：12で指定可能）
                - prefecture_code:都道府県コード（API：19, 21, 22で指定可能）
                - district_code:地区コード（API：19で指定可能）
                - save_file:geojsonファイル保存フラグ（すべてのAPIで指定可能）
                - output_dir:geojsonファイル保存先フォルダパス（すべてのAPIで指定可能）

                
                【概要】
                - 返却内容は、取得結果と不動産ライブラリの地図表示用URLです。取得結果がない場合でもURLは返却します。
                - api_resultsに各APIの結果（geojson)が格納され、返却時は例えば「地価公示のデータは2件取得できました。」の文言の後にgeojsonを返します。
                - 不動産情報ライブラリのAPIを呼び出すためのツールです。
                - ユーザーは「緯度・経度・その他任意パラメータ」を自然言語で指定するだけで利用できます。
                - サーバ内部では、指定した緯度・経度・距離から必要なXYZタイル（z, x, y）を計算し、APIを呼び出します。
                - 不動産ライブラリから返却されるデータのタイプによって仕様が変わります。（返却タプ別概要に記載）結果返却時に説明してください。

                【返却タイプ別概要】
                ■ポイントデータ
                 - 425m 以内の距離のみ検索可能です（API仕様および運用ポリシーに基づく制約）。指定しない場合はデフォルトで425mが使用されます。
                 - XYZ タイル単位でデータを返すため、このツールでは distance をカバーする複数タイルを内部で取得し、
                  中心地点からの実距離でフィルタした上で返却します。
                 - distance は 425m を上限とします。これを超える値が指定された場合はエラーとして扱います。
                - 該当API：2,3,9,10,11,12,17,18,

                ■ポリゴンデータ
                - 検索した緯度経度と重なるポリゴンデータのみ返却します。
                - 該当API：4,5,6,7,8,13,14,16,19,20,21,22,23,24,25,26,27,28,29,30（29のみラインデータを含む場合があります。）

                ■ラインデータ
                - ポイントデータの概要と同様。
                - 該当API：15,29 (29のみポリゴンデータを含む場合があります。)
                

                ■その他
                - 座標情報がないため、地名でフィルタリングをしています。
                - API結果に座標情報を付与しています。（該当API：1）


                【主な用途の例】
                - 「緯度35.681, 経度139.767の地価公示と都市計画区域のデータが欲しい」
                - 「この座標の半径100m以内の地価公示ポイントを一覧で教えて」
                
                """.strip(),
    inputSchema={
        "type": "object",
        "properties": {
            "lat": {
                "type": "number",
                "description": "検索の中心となる地点の緯度（10進法、小数）。例: 35.681236",
            },
            "lon": {
                "type": "number",
                "description": "検索の中心となる地点の経度（10進法、小数）。例: 139.767125",
            },
            "target_apis": {
                "type": "array",
                "items": {"type": "number"},
                "description": (
                    "呼び出すAPI番号。(例：[3,4,5])"
                    "未指定または空配列の場合は、全APIを取得します。(例：[])"
                ),
            },
            "distance": {
                "type": "number",
                "description": (
                    "中心地点からの検索距離（メートル）。（任意）"
                    "この値は 0〜425[m] の範囲で指定できます。425m を超える場合はエラーになります。"
                    "target_apiが1,2,3,9,10,11,12,15,17,18,29のとき有効。"
                ),
                "default": 425.0,
                "maximum": 425.0,
            },
            "price_classification": {
                "type": "string",
                "description": (
                    "target_apiが1のとき有効。"
                    "価格情報区分コード（任意）。\n"
                    '  "01": 不動産取引価格情報のみ, "02": 成約価格情報のみ, 未指定: 不動産取引価格情報と成約価格情報の両方'
                ),
            },
            "year": {
                "type": "number",
                "description": (
                    "対象年（4桁の西暦）。1995〜最新年の範囲で指定可能です。"
                    "未指定の場合は 2024 年として処理します。"
                    "target_apiが1,2,3のとき有効。"
                ),
            },
            "quarter": {
                "type": "number",
                "description": (
                    "target_apiが1のとき有効。"
                    "取引時期（四半期）。（任意）\n"
                    '  "1":1月～3月,"2":4月～6月,"3":7月～9月,"4":10月～12月'
                ),
            },
            "land_price_classification": {
                "type": "string",
                "description": (
                    "target_apiが3のとき有効。"
                    "地価情報区分コード。（任意）\n"
                    '  "0"  : 国土交通省地価公示のみ\n'
                    '  "1"  : 都道府県地価調査のみ\n'
                    "  (未指定の場合は、地価公示＋地価調査の両方）"
                ),
                "enum": ["0", "1"],
            },
            "language": {
                "type": "string",
                "description": (
                    "target_apiが1のとき有効。"
                    "出力結果の言語。（任意）\n"
                    '  "ja"  : 日本語\n'
                    '  "en"  : 英語\n'
                    "  (未指定の場合は、日本語）"
                ),
            },
            "division": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが2のとき有効。"
                    "用途区分（任意）。文字列の配列で指定。\n"
                    '  "00": 住宅地, "03": 宅地見込地, "05": 商業地, "07": 準工業地,\n'
                    '  "09": 工業地, "10": 市街地調整区域内現況宅地,\n'
                    '  "13": 現況林地, "20": 林地（都道府県地価調査）,未指定：すべて\n'
                    '  例: ["00", "05"]'
                ),
            },
            "use_category_code": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが3のとき有効。"
                    "用途区分コード（任意）。カンマ区切り指定可。\n"
                    '  "00": 住宅地, "03": 宅地見込地, 05: 商業地, 07: 準工業地,\n'
                    "  09: 工業地, 10: 市街地調整区域内現況宅地,\n"
                    "  13: 現況林地（公示のみ）, 20: 林地（調査のみ）,未指定：すべて"
                ),
            },
            "administrative_area_code": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが7,8,12,16,17,21,22,30のとき有効。"
                    "行政区域コード（任意）。カンマ区切り指定可。"
                    " 形式は数字5桁（文字列）"
                ),
            },
            "welfare_facility_class_code": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが12のとき有効。"
                    "福祉施設大分類コード（任意）。カンマ区切り指定可。\n"
                    "  01: 保護施設, 02: 老人福祉施設, 03: 障害者支援施設等, 04: 身体障害者社会参加支援施設,\n"
                    "  05: 児童福祉施設等, 06: 母子・父子福祉施設,99: その他の社会福祉施設等"
                    " 形式は数字2桁（文字列）"
                ),
            },
            "welfare_facility_middle_class_code": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが12のとき有効。"
                    "福祉施設中分類コード（任意）。カンマ区切り指定可。"
                    " 形式は数字4桁（文字列）"
                ),
            },
            "welfare_facility_minor_class_code": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが12のとき有効。"
                    "福祉施設小分類コード（任意）。カンマ区切り指定可。"
                    " 形式は数字6桁（文字列）"
                ),
            },
            "prefecture_code": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが19, 21, 22のとき有効。"
                    "都道府県コード（任意）。カンマ区切り指定可。"
                    " 形式は数字2桁（文字列）"
                ),
            },
            "district_code": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "target_apiが19のとき有効。"
                    "地区コード（任意）。カンマ区切り指定可。"
                    " 形式は数字1桁または数字2桁（文字列）。1桁目が0のものについては、0を取り除いた値で指定。"
                ),
            },
            "save_file": {
                "type": ["boolean", "null"],
                "description": (
                    "取得結果のgeojsonファイルを任意のフォルダに保存するかどうかのフラグ。指定がない場合はNoneとする。"
                    "true：ファイル保存する、false:保存しない、None：ユーザ確認。"
                    "save_fileがNoneの場合は、必ず「取得結果のファイルは保存しますか？」とユーザーに確認してください。"
                    "保存する場合（save_file=true）は保存先フォルダをユーザに返却する。"
                ),
            },
            "output_dir": {
                "type": "string",
                "description": "保存先ディレクトリ。（任意）。",
            },
        },
        "required": ["lat", "lon", "target_apis"],
    },
)
