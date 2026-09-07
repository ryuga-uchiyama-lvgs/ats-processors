# ATS Processors - 統合クローリングシステム

このフォルダには、ATS（採用管理システム）および関連求人サイトからデータを収集する処理をまとめています。

## 📁 ディレクトリ構成

```
ats-processors/
├── ats.py                  # ATSメインスクリプト（HRMOS/Talentio/JobCan）
├── rikunabi.py            # リクナビスクレイパー
├── config.yaml            # ATS認証設定ファイル
│
├── utils/                 # 共通ユーティリティ
│   ├── login_direct.py    # ログイン処理（各ATS対応）
│   ├── scraping.py        # スクレイピング処理
│   ├── data_format.py     # データフォーマット統一
│   └── __init__.py
│
├── herp/                  # Herpスクレイパー
│   ├── herp.py           # Herpメインスクリプト
│   ├── herp.txt          # HerpURL一覧（旧）
│   ├── herp_urls_new.txt # HerpURL一覧（新）
│   └── output_herp_jobs/ # Herp出力CSVファイル
│
├── output/               # 各ATS出力ディレクトリ
│   ├── hrmos/           # HRMOS出力
│   ├── talentio/        # Talentio出力
│   ├── jobcan/          # JobCan出力
│   └── rikunabi/        # リクナビ出力
│
└── README.md            # このファイル
```

---

## 🚀 使用方法

### 1. ATS データ収集（ats.py）

複数のATSから求人データを一括収集します。

#### 実行方法

```bash
# ats.pyを編集してメディアを選択
vim ats.py
# use_media = "hrmos"  # または "talentio", "jobcan"

# 実行
python ats.py
```

#### 対応ATS

| ATS          | URL                           | カテゴリ                       |
| ------------ | ----------------------------- | ------------------------------ |
| **HRMOS**    | https://hrmos.co/agent/       | WEB, IN_DS, CRS, CRG, コンサル |
| **Talentio** | https://agent.talentio.com/   | WEB, IN_DS, CRS, CRG, コンサル |
| **JobCan**   | https://ats.jobcan.jp/agents/ | WEB, IN_DS, CRS, CRG, コンサル |

#### 出力先

```
output/{media_type}/{media}_{category}_item_list_{date}.csv
```

**例:**

```
output/hrmos/hrmos_WEB_item_list_2026-03-18.csv
output/talentio/talentio_CRS_item_list_2026-03-18.csv
```

#### 出力フォーマット

| 列名             | 説明                             |
| ---------------- | -------------------------------- |
| 取得日           | データ取得日（YYYY-MM-DD）       |
| 媒体名           | ATS名（hrmos, talentio, jobcan） |
| 会社名           | 企業名                           |
| 求人ページ用     | 求人詳細URL                      |
| 募集職種         | 職種名                           |
| 求人カテゴリ     | カテゴリ（WEB, IN_DS, CRS等）    |
| 雇用形態         | 正社員、契約社員等               |
| 募集人数         | 募集人数                         |
| 概要・業務内容   | 業務内容詳細                     |
| 必須スキル・経験 | 必須要件                         |
| 歓迎スキル・経験 | 歓迎要件                         |
| 求める人物像     | 求める人物像                     |
| 勤務時間         | 勤務時間                         |
| 休日・休暇       | 休日情報                         |
| 想定給与         | 給与情報                         |

---

### 2. リクナビデータ収集（rikunabi.py）

リクナビNEXTから求人データを収集します。

#### 実行方法

```bash
python rikunabi.py
```

#### カテゴリ設定

スクリプト内で定義されたカテゴリごとに実行：

```python
CATEGORY_CONFIG = [
    {"カテゴリ名": "WEB", "ID": "xxxxx@example.com", "PASS": "********"},
    {"カテゴリ名": "IN_DS", "ID": "xxxxx@example.com", "PASS": "********"},
    {"カテゴリ名": "CRS", "ID": "xxxxx@example.com", "PASS": "********"},
    {"カテゴリ名": "CRG", "ID": "xxxxx@example.com", "PASS": "********"},
    {"カテゴリ名": "コンサル", "ID": "xxxxx@example.com", "PASS": "********"},
]
```

#### 出力先

```
output/rikunabi/rikunabi_{category}_item_list_{date}.csv
```

#### 出力フォーマット

| 列名               | 説明               |
| ------------------ | ------------------ |
| 企業名             | 企業名             |
| 求人名             | 求人タイトル       |
| 募集要項ファイル名 | PDFファイル名      |
| 募集要項リンク     | PDFダウンロードURL |
| 企業からのコメント | 企業コメント       |

---

### 3. Herpデータ収集（herp/herp.py）

Herpエージェント向け求人サイトからデータを収集します。

#### 実行方法

```bash
cd herp
python herp.py              # 全カテゴリ（約2時間）
python herp.py CRG          # カテゴリ指定（複数可: python herp.py CRS WEB）
HERP_SHOW_BROWSER=1 python herp.py CRG   # ブラウザ画面を出して実行（既定は非表示）
```

#### ログイン（2026/8/5〜必須）

ID/PASS は `../config.yaml` の `login.accounts`（HRMOS 等と共通）から読む。旧 `herp/password.txt` は残っていればフォールバックとして読む。

#### URL設定

ログイン後の招待一覧（`/p/invitations`）から毎回取り直す。`herp.py`内の`HERP_URLS`リストは招待一覧が取れなかったときのフォールバック：

```python
HERP_URLS = [
    ("CRG", "株式会社MIXI", "https://agent.herp.cloud/p/..."),
    ("CRS", "株式会社UPSIDER", "https://agent.herp.cloud/p/..."),
    ("WEB", "株式会社MIXI", "https://agent.herp.cloud/p/..."),
    # ... 他多数
]
```

#### 出力先

```
herp/output_herp_jobs/herp-{category}-{date}.csv
```

**例:**

```
herp/output_herp_jobs/herp-WEB-20260318.csv
herp/output_herp_jobs/herp-CRS-20260318.csv
```

#### 出力フォーマット

Herpの求人詳細データ（カテゴリ、企業名、求人URL、職種、業務内容等）

#### 検算

カテゴリ単位で CSV を書いた直後に「0件 / 案件名が空 / 詳細列なし / 仕事概要の充足率50%未満」を検査し、1つでも該当すれば `🔴 検算NG` を表示して終了コード1で終わる。NG のカテゴリは納品せず、そのカテゴリだけ再実行する。

---

## ⚙️ 設定ファイル

### config.yaml

各ATSへのログイン情報を管理します。

```yaml
login:
  url: "https://hrmos.co/agent/login"
  talentio_url: "https://agent.talentio.com/login"
  jobcan_url: "https://ats.jobcan.jp/agents/sign_in"

  accounts:
    WEB:
      email: "xxxxx@example.com"
      password: "********"

    IN_DS:
      email: "xxxxx@example.com"
      password: "********"

    CRS:
      email: "xxxxx@example.com"
      password: "********"

    CRG:
      email: "xxxxx@example.com"
      password: "********"

    コンサル:
      email: "xxxxx@example.com"
      password: "********"
```

**⚠️ セキュリティ注意:**

- このファイルはGit管理から除外してください
- 本番環境では環境変数を使用してください

---

## 🔧 共通ユーティリティ（utils/）

### login_direct.py

各ATSへのログイン処理を提供

```python
def login_hrmos(email, password, login_url)
def login_talentio(email, password, login_url)
def login_jobcan(email, password, login_url)
```

**特徴:**

- Selenium + Chrome WebDriver使用
- ヘッドレスモード対応
- ログイン成功確認機能付き
- エラーハンドリング実装

### scraping.py

各ATSからのデータ抽出処理

```python
def crawl_site(driver, date_str, media_name, filename)      # HRMOS用
def crawl_talentio(driver, date_str, media_name, filename)  # Talentio用
def crawl_jobcan(driver, date_str, media_name, filename)    # JobCan用
```

**特徴:**

- ページネーション対応
- 複数タブ制御
- エラーリカバリ機能
- CSV自動出力

### data_format.py

データフォーマット統一処理（共通カラム定義など）

---

## 📊 実行フロー

### ATSクローリング（ats.py）

```
1. config.yaml読み込み
   ↓
2. メディア選択（hrmos/talentio/jobcan）
   ↓
3. カテゴリごとにループ（WEB, IN_DS, CRS, CRG, コンサル）
   ↓
4. ログイン処理（utils/login_direct.py）
   ↓
5. スクレイピング処理（utils/scraping.py）
   ↓
6. CSV出力（output/{media}/{media}_{category}_item_list_{date}.csv）
   ↓
7. ドライバー終了、次のカテゴリへ
```

### リクナビクローリング（rikunabi.py）

```
1. Playwright起動
   ↓
2. カテゴリごとにループ
   ↓
3. ログイン
   ↓
4. 求人一覧ページアクセス
   ↓
5. 企業ごとに求人情報取得
   ↓
6. CSV出力（output/rikunabi/rikunabi_{category}_item_list_{date}.csv）
```

### Herpクローリング（herp/herp.py）

```
1. Playwright起動
   ↓
2. HERP_URLsリストをループ
   ↓
3. 各URLにアクセス
   ↓
4. 求人詳細データ抽出
   ↓
5. カテゴリ別にデータ蓄積
   ↓
6. カテゴリごとにCSV出力（herp/output_herp_jobs/herp-{category}-{date}.csv）
```

---

## 🛠️ トラブルシューティング

### よくあるエラー

#### 1. ログインエラー

```
❌ ログイン失敗：{category} | エラー内容: ...
```

**対処法:**

- `config.yaml`の認証情報を確認
- ATSサイトがメンテナンス中でないか確認
- ヘッドレスモードをOFFにしてデバッグ

#### 2. WebDriver起動エラー

```
selenium.common.exceptions.WebDriverException
```

**対処法:**

```bash
# ChromeDriverを最新化
pip install --upgrade webdriver-manager

# または手動でインストール
brew install chromedriver
```

#### 3. Playwrightエラー

```
playwright._impl._api_types.Error: Browser closed
```

**対処法:**

```bash
# Playwrightブラウザ再インストール
playwright install chromium
```

#### 4. インポートエラー

```
ModuleNotFoundError: No module named 'utils'
```

**対処法:**

- スクリプトは必ず`ats-processors/`ディレクトリで実行
- Python pathに`ats-processors`を追加

#### 5. 出力ディレクトリエラー

```
FileNotFoundError: [Errno 2] No such file or directory: 'output/...'
```

**対処法:**

```bash
# 出力ディレクトリを手動作成
mkdir -p output/hrmos output/talentio output/jobcan output/rikunabi
```

---

## 📦 依存パッケージ

### 必須パッケージ

```bash
pip install selenium
pip install webdriver-manager
pip install playwright
pip install pandas
pip install pyyaml
pip install beautifulsoup4
```

### Playwright初期設定

```bash
# ブラウザインストール
playwright install chromium
```

---

## 🔐 セキュリティベストプラクティス

### 認証情報管理

```bash
# .gitignoreに追加
echo "config.yaml" >> .gitignore
echo "*.csv" >> .gitignore
echo "output/" >> .gitignore
```

### 環境変数での管理（推奨）

```python
import os

email = os.getenv("ATS_EMAIL")
password = os.getenv("ATS_PASSWORD")
```

```bash
# 実行時に環境変数設定
export ATS_EMAIL="your-email@example.com"
export ATS_PASSWORD="your-password"
python ats.py
```

---

## 📈 パフォーマンス最適化

### ヘッドレスモード使用

```python
options.add_argument('--headless=new')  # メモリ節約
```

### 並列実行

```bash
# 複数カテゴリを並列実行
python ats.py &  # hrmos
# スクリプトを変更してtalentio実行 &
# 等
```

### タイムアウト設定

```python
# ページロード待機時間を調整
WebDriverWait(driver, 10)  # 10秒待機
```

---

## 📝 ログ管理

### 実行ログ

```bash
# 標準出力をファイルに保存
python ats.py > logs/ats_$(date +%Y%m%d).log 2>&1

# リアルタイムで確認
tail -f logs/ats_$(date +%Y%m%d).log
```

---

## 🔄 定期実行設定（cron）

```bash
# crontabを編集
crontab -e

# 毎日午前2時に実行
0 2 * * * cd /path/to/ats-processors && python ats.py >> logs/cron.log 2>&1

# 毎週月曜午前3時にリクナビ実行
0 3 * * 1 cd /path/to/ats-processors && python rikunabi.py >> logs/rikunabi_cron.log 2>&1
```

---

## 📚 関連リンク

### ATS公式サイト

- [HRMOS](https://hrmos.co/)
- [Talentio](https://talentio.com/)
- [JobCan採用管理](https://ats.jobcan.ne.jp/)
- [Herp](https://herp.cloud/)

### 求人サイト

- [リクナビNEXT](https://next.rikunabi.com/)

### 技術ドキュメント

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Playwright Documentation](https://playwright.dev/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. **エラーログ**: 標準出力のエラーメッセージを確認
2. **認証情報**: config.yamlの設定を再確認
3. **環境**: Python、Selenium、Playwrightのバージョン確認
4. **ネットワーク**: インターネット接続を確認

---

**最終更新日:** 2026年3月18日  
**バージョン:** 1.0.0  
**メンテナ:** ATS Crawling Team
