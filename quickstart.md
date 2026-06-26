# Quickstart（CLI セットアップ手順）

エンジニア向けの、ターミナルだけで完結するセットアップ・実行手順です。
非エンジニア向けの `.command` / `.bat`（ダブルクリック）を使わず、`uv` で環境を作って直接実行します。

このリポジトリには 2 つのプロジェクトがあります。必要な方だけセットアップしてください。

| プロジェクト | 内容 | 主な依存 |
| --- | --- | --- |
| `毎日の取得/` | ATS（HRMOS / Talentio / JobCan）＋リクナビ＋HERP の日次クローラ | pandas, pyyaml, selenium, webdriver-manager, playwright |
| `月次集計-WL/` | 4 媒体スクレイプ＋doda 手動取得 → 重複削除して納品フォルダ生成 | playwright |

実行環境（Python 本体含む）はすべて `uv` が用意します。マシン側に Python を入れる必要はありません。

---

## 0. 前提：uv のインストール

```bash
# 未インストールなら入れる（数十秒）
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

# PATH を通す（インストール直後は必要）
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

uv --version   # 確認
```

### 社内ネットワーク（SSL 証明書エラー）対策

社内プロキシ（Zscaler 等）が SSL 検査を挟む環境では、`uv` が証明書を信頼できず
`invalid peer certificate: UnknownIssuer` で失敗します。`uv` は標準では macOS キーチェーンを
参照しないためです。**`UV_NATIVE_TLS=1` を付けると OS の証明書ストア（社内ルート証明書が入っている場所）を
参照する**ようになり、たいてい解決します。

```bash
export UV_NATIVE_TLS=1
```

> このシェルで `uv` を使う前に 1 回 export しておけば、以降の `uv` コマンドすべてに効きます。
> 恒久的にしたい場合は `~/.zshrc` に追記してください。
>
> それでも `UnknownIssuer` が出る場合は、キーチェーンに社内ルート証明書が入っていない可能性があります。
> 情シスに CA 証明書を確認のうえ、ファイルがあれば `export SSL_CERT_FILE=/path/to/ca.pem` で指定します。

---

## 1. 毎日の取得（ATS クローラ）

### 1-1. 環境構築

```bash
cd 毎日の取得

# Python 3.12 の仮想環境を作成（プログラム本体/venv に作られる）
uv venv --clear --python 3.12 プログラム本体/venv

# 依存パッケージをインストール
uv pip install --python プログラム本体/venv/bin/python \
  pandas pyyaml selenium webdriver-manager playwright

# 自動操作用ブラウザ（リクナビ・HERP で使用）を取得
プログラム本体/venv/bin/python -m playwright install chromium
```

以降、`プログラム本体/venv/bin/python` を Python として使います。
`source プログラム本体/venv/bin/activate` で有効化すれば、単に `python` でも実行できます。

### 1-2. 認証ファイルの配置

両ファイルとも **`毎日の取得/プログラム本体/` 直下**（= `ats.py` / `rikunabi.py` と同じ場所）に置きます。
`config.yaml` は `ats.py` がカレントディレクトリから、`credentials.yaml` は `rikunabi.py` が
スクリプトと同じ場所から読み込みます。どちらも `.gitignore` 済みでコミットされません。

```bash
cd プログラム本体

# リクナビ用 認証情報（テンプレートから作成して ID/PASS を記入）
cp credentials.example.yaml credentials.yaml
$EDITOR credentials.yaml
```

`config.yaml`（ATS 用）はテンプレートが無いため、以下の形式で新規作成します。

```yaml
# 毎日の取得/プログラム本体/config.yaml
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

### 1-3. 実行

いずれも `プログラム本体/` をカレントにして実行します（`config.yaml` と相対パス出力のため）。

```bash
cd 毎日の取得/プログラム本体
PY=venv/bin/python

# ATS（--media で媒体を指定。未指定時は talentio）
$PY ats.py --media hrmos
$PY ats.py --media talentio
$PY ats.py --media jobcan

# リクナビ（全カテゴリ。credentials.yaml の rikunabi 配下を順に処理）
$PY rikunabi.py

# リクナビ（カテゴリを 1 つだけ指定）
$PY rikunabi.py WEB

# HERP（herp/ サブフォルダで実行。cd 後はひとつ上の venv を指す）
cd herp && ../$PY herp.py
```

#### 出力先

```
毎日の取得/プログラム本体/output/{media}/{media}_{category}_item_list_{YYYY-MM-DD}.csv
毎日の取得/プログラム本体/output/rikunabi/rikunabi_{category}_item_list_{YYYYMMDD}.csv
毎日の取得/プログラム本体/herp/output_herp_jobs/herp-{category}-{YYYYMMDD}.csv
```

> 曜日ごとの実行内容（月: HRMOS+リクナビ+HERP / 火木: HRMOS+Talentio / 水金: HRMOS+JobCan）は
> `実行する.command` のロジックを参照してください。CLI では上記コマンドを必要な分だけ叩きます。

---

## 2. 月次集計-WL

### 2-1. 環境構築

```bash
cd 月次集計-WL

uv venv --clear --python 3.12 プログラム本体/venv
uv pip install --python プログラム本体/venv/bin/python playwright
プログラム本体/venv/bin/python -m playwright install chromium
```

各媒体サブフォルダにも `requirements.txt` がありますが、実際に必要なのは `playwright` のみです
（`②集計する.command` と同じ構成）。

### 2-2. その① 4 媒体のスクレイプ

各スクリプトをそれぞれのフォルダで実行します（全部で 30 分〜2 時間）。

```bash
cd 月次集計-WL/プログラム本体
PY=venv/bin/python

(cd atGP               && ../$PY scrape_atgp.py)
(cd LITALICO           && ../$PY scrape_snabi_jobs.py)
(cd BABNAVI            && ../$PY scraper.py)
(cd マイナビパートナーズ && ../$PY scraper.py)
```

### 2-3. その② doda チャレンジ（手動取得）

doda チャレンジは自動化対象外のため手動です。

1. ブラウザで doda チャレンジの検索結果ページを開く
2. 「もっと見る」を出なくなるまで押す
3. 求人一覧の HTML をコピーし、`月次集計-WL/dodaここに貼る.txt` に貼り付けて保存

### 2-4. その③ 変換・集計

```bash
cd 月次集計-WL/プログラム本体
PY=venv/bin/python

# doda の貼り付け HTML を CSV に変換
cp ../dodaここに貼る.txt doda-challenge/doda-challenge.txt
(cd doda-challenge && ../$PY parse_jobs.py)

# 5 媒体をまとめて正規化・企業名重複削除（引数は集計日 YYYYMMDD、省略時は今日）
$PY monthly_dedup.py            # 今日の日付で集計
# $PY monthly_dedup.py 20260601 # 日付を明示したい場合
```

#### 出力先

`プログラム本体/{YYYYMMDD}_集計/` に正規化済み CSV と統合企業名一覧（計 7 ファイル）が生成されます。
7 ファイル揃っていれば、このフォルダを丸ごと Google Drive にアップロードして完了です。
途中で `[警告]` / `[SKIP]` が出た媒体は、その媒体の取得からやり直してください。

---

## 3. トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `invalid peer certificate: UnknownIssuer`（uv） | `export UV_NATIVE_TLS=1` を設定してから再実行（→ 0 章） |
| `FileNotFoundError: config.yaml` | `毎日の取得/プログラム本体/` をカレントにして実行しているか確認 |
| `credentials.yaml が見つかりません` | `cp credentials.example.yaml credentials.yaml` で作成し ID/PASS を記入 |
| `playwright ... Browser closed` / ブラウザ無し | `venv/bin/python -m playwright install chromium` を再実行 |
| `ModuleNotFoundError: No module named 'utils'` | `ats.py` は必ず `プログラム本体/` フォルダ内で実行 |
| 月次でファイルが 7 個に満たない | 不足媒体の「その①」スクレイプからやり直す |
