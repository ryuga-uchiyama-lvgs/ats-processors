# atGP求人情報スクレイピングツール

atGPの求人サイトから求人情報を取得するPythonスクリプトです。

## 機能

- prefecture-id.csvに記載された都道府県の求人情報を自動取得
- ページネーション対応（全ページを自動巡回）
- 求人情報を詳細に取得（タイトル、会社名、職種、勤務地、給与など）
- JSON・CSV形式で出力

## 取得できる情報

各求人について以下の情報を取得します：

- **updateDate**: 更新日
- **isNew**: NEW表示の有無
- **title**: 求人タイトル
- **detailUrl**: 求人詳細ページのURL
- **companyName**: 会社名
- **categoryTags**: カテゴリタグ（正社員登用あり、転勤なし等）
- **jobType**: 職種
- **location**: 勤務地
- **employmentType**: 雇用形態
- **salary**: 給与
- **companyPageUrl**: 企業ページのURL
- **prefecture_id**: 都道府県ID
- **prefecture_name**: 都道府県名
- **scraped_at**: 取得日時

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. Playwrightブラウザのインストール

```bash
playwright install chromium
```

## 使い方

### prefecture-id.csvの設定

`prefecture-id.csv`に取得したい都道府県のIDと名前を記載します。

デフォルトでは以下の都道府県が設定されています：

```csv
prefecture_id,prefecture_name
11,埼玉県
12,千葉県
13,東京都
14,神奈川県
23,愛知県
27,大阪府
40,福岡県
```

### スクリプトの実行

```bash
python scrape_atgp.py
```

実行すると、以下のファイルが生成されます：

- `atgp_jobs_YYYYMMDD_HHMMSS.json` - JSON形式の結果
- `atgp_jobs_YYYYMMDD_HHMMSS.csv` - CSV形式の結果

## 出力例

### JSON形式

```json
[
  {
    "updateDate": "更新日：2025年11月11日",
    "isNew": true,
    "title": "在宅併用相談可（週1～2出社）【音楽好きな方お待ちしております！】労務関連経験がある方の募集",
    "detailUrl": "https://www.atgp.jp/search/top/search_result_detail/xxxxx",
    "companyName": "ユニバーサル ミュージック合同会社",
    "categoryTags": ["正社員登用あり", "転勤なし"],
    "jobType": "HRアシスタント 総務・人事",
    "location": "東京都 渋谷区 【最寄り駅】 原宿駅、明治神宮前〈原宿〉駅",
    "employmentType": "契約社員(登用あり)",
    "salary": "●月給制 月収： 250,000円 ~ 400,000円 (年収： 350万円 ~ 560万円 )",
    "companyPageUrl": "https://www.atgp.jp/search/top/company_recruit/xxxxx",
    "prefecture_id": "13",
    "prefecture_name": "東京都",
    "scraped_at": "2025-11-11T12:00:00.000000"
  }
]
```

## 注意事項

- スクレイピング時はサーバーに負荷をかけないよう、適切な間隔（1秒）を設けています
- robots.txtやサイトの利用規約を確認し、適切に使用してください
- 取得したデータの利用については、atGPの利用規約に従ってください

## カスタマイズ

### ヘッドレスモードの切り替え

スクリプト内の`AtGPScraper`の初期化で`headless`を`False`に設定すると、ブラウザの動作を確認できます：

```python
scraper = AtGPScraper(headless=False)
```

### 待機時間の調整

`asyncio.sleep()`の値を調整することで、ページ間の待機時間を変更できます。
