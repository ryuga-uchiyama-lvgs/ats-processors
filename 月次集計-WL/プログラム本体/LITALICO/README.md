# LITALICO Snabi 求人情報スクレイピングツール

このツールは、[LITALICO仕事ナビ（Snabi）](https://snabi.jp/)の東京都の求人情報を取得するPythonスクリプトです。

## 機能

- 東京都の全ての求人情報をスクレイピング
- ページネーションに対応（全53ページ）
- 取得した情報をJSON・CSV形式で保存
- 合計1050件以上の求人情報を取得可能

## 取得できる情報

各求人について、以下の情報を取得します：

- **id**: 求人ID
- **href**: 求人詳細ページのURL
- **employmentType**: 雇用形態（例：契約社員、正社員など）
- **title**: 求人タイトル
- **companyInfo**: 会社情報
- **jobDescription**: 職種の説明
- **salary**: 給与情報
- **location**: 勤務地
- **accommodationTags**: 合理的配慮のタグリスト

## セットアップ

### 1. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. Playwrightブラウザのインストール

```bash
playwright install chromium
```

## 使い方

### 基本的な実行方法

```bash
python scrape_snabi_jobs.py
```

実行すると、以下のファイルが生成されます：

- `snabi_jobs_YYYYMMDD_HHMMSS.json`: JSON形式の求人データ
- `snabi_jobs_YYYYMMDD_HHMMSS.csv`: CSV形式の求人データ

### 実行例

```bash
$ python scrape_snabi_jobs.py

============================================================
LITALICO Snabi 求人情報スクレイピング
============================================================
アクセス中: https://snabi.jp/recruitments/prefecture-13
総ページ数: 53

ページ 1/53 を処理中...
  20 件の求人を取得しました（累計: 20 件）

ページ 2/53 を処理中...
  20 件の求人を取得しました（累計: 40 件）
...
```

## 出力ファイル形式

### JSON形式

```json
[
  {
    "id": "6022",
    "href": "https://snabi.jp/recruitments/6022",
    "employmentType": "契約社員",
    "title": "アプリケーションエンジニア/正社員登用制度あり/フレックス制/年間休日125日◎",
    "companyInfo": "ソーバル株式会社のエンジニア/契約社員の障害者雇用求人(東京都_品川区）",
    "jobDescription": "【エンジニア】アプリケーションエンジニアとして...",
    "salary": "想定年収：300万円〜400万円月給制：22万5000円〜30万円",
    "location": "東京都品川区北品川5-9-11 大崎MTビル(本社)",
    "accommodationTags": [
      "階段昇降なし",
      "ヘッドホン・耳栓利用可",
      "拡大鏡使用可能"
    ]
  }
]
```

### CSV形式

CSVファイルは、上記の全てのフィールドを列として持ちます。`accommodationTags`はカンマ区切りの文字列として保存されます。

## カスタマイズ

### 異なる都道府県をスクレイピングする場合

`scrape_snabi_jobs.py`の`base_url`を変更してください：

```python
# 例：神奈川県（prefecture-14）の求人を取得
jobs = await scrape_all_jobs("https://snabi.jp/recruitments/prefecture-14")
```

### 待機時間の調整

サーバーへの負荷を考慮して、ページ読み込み後の待機時間を調整できます：

```python
await page.wait_for_timeout(2000)  # 2秒待機（ミリ秒単位）
```

## 注意事項

- このスクリプトは教育目的で作成されています
- スクレイピングを実行する際は、対象サイトの利用規約を確認してください
- サーバーに過度な負荷をかけないよう、適切な間隔でリクエストを行ってください
- 取得したデータの使用については、各自の責任で行ってください

## 技術仕様

- **Python**: 3.7以上推奨
- **Playwright**: 非同期処理による高速なスクレイピング
- **出力形式**: JSON、CSV

## トラブルシューティング

### エラー: `playwright not found`

```bash
pip install playwright
playwright install chromium
```

### エラー: タイムアウト

ネットワークが遅い場合は、待機時間を増やしてください：

```python
await page.wait_for_timeout(5000)  # 5秒に変更
```

### CSVファイルの文字化け

Excel で開く場合は、UTF-8 BOM 付きで保存するか、Google Sheets などを使用してください。
