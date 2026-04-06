# MLIT Geospatial MCP Server

## 概要
Claude MCPから不動産情報ライブラリAPIを統合的に呼び出すためのMCPサーバです。
大規模言語モデル（LLM）と直接連携し、対話形式で直感的に不動産情報ライブラリのデータを検索・取得することが可能になります。

## 主な機能
以下の不動産情報ライブラリAPIのデータを提供します：  
`get_multi_api`（不動産情報ライブラリAPIを統合的に呼び出すことが可能です。）

**【利用可能なAPI】**
- 不動産価格（取引価格・成約価格）情報取得API
- 鑑定評価書情報API
- 地価公示・地価調査のポイント（点）API
- 都市計画決定GISデータ（都市計画区域・区域区分）API
- 都市計画決定GISデータ（用途地域）API
- 都市計画決定GISデータ（立地適正化計画）API
- 国土数値情報（小学校区）API
- 国土数値情報（中学校区）API
- 国土数値情報（学校）API
- 国土数値情報（保育園・幼稚園等）API
- 国土数値情報（医療機関）API
- 国土数値情報（福祉施設）API
- 国土数値情報（将来推計人口250mメッシュ）API
- 都市計画決定GISデータ（防火・準防火地域）API
- 国土数値情報（駅別乗降客数）API
- 国土数値情報（災害危険区域）API
- 国土数値情報（図書館）API
- 国土数値情報（市区町村役場及び集会施設等）API
- 国土数値情報（自然公園地域）API
- 国土数値情報（大規模盛土造成地マップ）API
- 国土数値情報（地すべり防止地区）API
- 国土数値情報（急傾斜地崩壊危険区域）API
- 都市計画決定GISデータ（地区計画）API
- 都市計画決定GISデータ（高度利用地区）API
- 国土交通省都市局（地形区分に基づく液状化の発生傾向図）API
- 国土数値情報（洪水浸水想定区域（想定最大規模））API
- 国土数値情報（高潮浸水想定区域）API
- 国土数値情報（津波浸水想定）API
- 国土数値情報（土砂災害警戒区域）API
- 国土数値情報（人口集中地区）API

##  動作環境
* OS：Windows 10 / 11 または macOS 13以降
* MCPホスト：Claude Desktopなど
* MCPサーバー実行環境：Python 3.10+
* メモリ：8GB以上推奨
* ストレージ：空き容量 1GB以上（キャッシュやログを含む）

## インストールとセットアップ

### 前提条件
以下は、Claude Desktopでの利用を想定した手順です。

### 手順

1. **Pythonをインストール**  
   **【Pythonがすでにインストールされているかを確認】**
   * コマンドプロンプトを起動してください。Windowsのスタートメニュー検索で 「cmd」 とタイプすると表示されます。
   * コマンドプロンプトを起動したら、C:¥～～～～> とでてきます。 > の後に続けて python と入力しEnterを押してください。  
   Python 3.10.X ～～ と表示があればインストールされています。手順2を実施してください。

   **【Pythonをインストール】**
   * Pythonをインストールしてください。（バージョンは、3.10以上をインストールしてください。）  
   Pythonの公式ダウンロードページ（[https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)）から、利用OSに合わせて3.10以上のインストーラーをダウンロードして、インストーラーを起動してください。
   * インストーラーの指示に従って、インストールを行ってください。  
      画面下部の「Add Python 3.x to PATH」のチェックボックスにチェックを入れてから、 Install Now を選択してください。  
      ※「Add Python 3.x to PATH」のチェックボックスにチェックを忘れてインストールした場合は、環境変数にPython.exeの場所を追加してください。

   * インストール後にコマンドプロンプトを再度起動して、> の後に続けて python と入力しEnterを押してください。  
      `>>>` と最後に表示されていれば、Pythonが起動している状態です。Python 3.10.X ～～ と表示があればOKです。  
      quit() と入力しEnterを押して、Pythonを終了してください。

2. **Claude Desktopをダウンロード・インストール**
   * Claudeの公式ダウンロードページ([https://claude.com/download](https://claude.com/download))にアクセスし、インストーラーをダウンロードしてください。
   * ダウンロードしたファイルを実行するとインストールが開始されます。  
      画面の案内に従って「始める」をクリックし、アカウント認証を行うことでインストールが完了します。

3. **不動産情報ライブラリのAPI利用申請**
   * 不動産情報ライブラリの公式ページ([https://www.reinfolib.mlit.go.jp/api/request/](https://www.reinfolib.mlit.go.jp/api/request/))にアクセスし、API利用申請をしてください。   

4. **ソースコードをcloneする**
   * コマンドプロンプトを起動して、任意のディレクトリに移動する（例：C:\Users\username\）
   * 以下のコマンドでcloneする（mlit-geospatial-mcpディレクトリが自動的に作成されます）
   ```bash
   git clone https://github.com/chirikuuka/mlit-geospatial-mcp.git
   cd mlit-geospatial-mcp
   ```
   ※cloneのURLは、githubにてページ上部の「code」ボタンからコピーできます

5. **仮想環境を作成 & 有効化**
   * 仮想環境の作成・有効化を実施する   
（ディレクトリはそのままmlit-geospatial-mcp上で実施）
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windowsの場合
   source .venv/bin/activate   # macOS/Linuxの場合
   ```
   (.venv) C:\Users\username\mlit-geospatial-mcp>の状態になれば成功です。

6. **依存ライブラリをインストール**

   ```bash
   pip install -r requirements.txt
   ```
   

7. **Claude Desktopの設定ファイルを開く**

   * Claude Desktopアプリの設定画面にある「開発者」メニューの「設定を編集」ボタンをクリックして`claude_desktop_config.json`を開く。
      * **Windows：** `C:\Users\<ユーザー名>\AppData\Roaming\Claude\claude_desktop_config.json`
      * **macOS：** `~/Library/Application Support/Claude/claude_desktop_config.json`

      ※初回インストール時は`claude_desktop_config.json`は存在しません。アプリの設定画面から設定ファイルを開くと自動的に作成されます。

8. **MCPサーバーの構成を追加**  
`claude_desktop_config.json`に下記を記載します。

   ```json
   {
      "mcpServers": {
         "mlit-geospatial-mcp": {
            "command": "......./mlit-geospatial-mcp/.venv/Scripts/python.exe",
            "args": [
               "....../mlit-geospatial-mcp/src/server.py"
            ],
            "env": {
               "LIBRARY_API_KEY": "your_api_key_here",
               "PYTHONUNBUFFERED": "1",
               "LOG_LEVEL": "WARNING"
            }
         }
      }
   }
   ```

   * `command`と`args`は必ず、実際のパスに変更してください。
   (例：C:/Users/username/mlit-geospatial-mcp/.venv/Scripts/python.exe)
   * `your_api_key_here`は必ず、手順3で取得したキーに置き換えてください。

9. **Claude Desktop を再起動**  
   Claude Desktopの左上にある「≡」のファイル＞終了をクリックして終了し、再度Claude Desktopを起動します。  
   ※Claude Desktopが起動しない場合は、タスクマネージャーで「タスクの終了」を実行した後、再度起動を試してください。
