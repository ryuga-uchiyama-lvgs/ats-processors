---
name: daily-run
description: 「毎日の取得」(HRMOS・Talentio・JobCan・リクナビ・HERP の求人データ取得)を、今日の曜日に合わせて実行し、結果を報告する。「今日の分の実行をお願いします」「今日の分を回して」「毎日の取得をやって」などの依頼で必ず使う。
---

# 毎日の取得(今日の分の実行)

`毎日の取得/実行する.bat` と同じ処理を、Claude がコマンドで直接実行する手順です。
ダブルクリック用の .bat は `pause` で止まるため使わず、Python を直接呼びます。

## 1. 今日が実行日か確認して、実行する媒体を決める

このスキルと同じフォルダの `check_day.py` で、実行しない日かを判定します。

- 土日
- 祝日(内閣府の祝日CSVを参照)
- 年末年始: 12/28〜1/4
- 夏季休暇: 8/12〜8/17

```bash
cd "<リポジトリ>/毎日の取得/プログラム本体"
PYTHONUTF8=1 ./venv/Scripts/python.exe ../../.claude/skills/daily-run/check_day.py
```

- `RUN <曜日番号>`(終了コード 0): 下の表に沿って実行する
- `SKIP 土日` / `SKIP 祝日 <祝日名>` / `SKIP 年末年始` / `SKIP 夏季休暇`(終了コード 1): **何も実行せず**、理由を伝えて終了する。休みの日はユーザーが応答できないため、確認も求めない
- `UNKNOWN ...`(終了コード 2): 祝日かどうか判定できないので**実行しない**。理由を報告して終了する

| 曜日 | 実行する媒体(上から順に) |
|---|---|
| 月 | HRMOS → リクナビ → HERP(1時間以上かかる) |
| 火・木 | HRMOS → Talentio |
| 水・金 | HRMOS → JobCan |

## 2. 事前チェック

- `毎日の取得/プログラム本体/venv/Scripts/python.exe` があること(無ければ「はじめにこれ.bat」が未実施なので、ユーザーに伝えて止まる)
- `毎日の取得/プログラム本体/config.yaml` があること(HRMOS・Talentio・JobCan・HERP のログイン情報。無ければ止まる)
- 月曜のみ: `毎日の取得/プログラム本体/credentials.yaml` があること(リクナビ用)

config.yaml・credentials.yaml の中身(ID/パスワード)は表示・引用しないでください。

## 3. 実行

作業フォルダは `毎日の取得/プログラム本体`、環境変数 `PYTHONUTF8=1` を付けて実行します。
時間がかかるので Bash の `run_in_background` で 1 つのコマンドにまとめて流し、終了通知を待ちます(途中でポーリングしない)。
ログは媒体ごとにスクラッチパッドのディレクトリへ書き出し、各媒体の終了コードを echo しておきます。
1 つの媒体が失敗しても、残りの媒体は続けて実行します。

```bash
cd "<リポジトリ>/毎日の取得/プログラム本体"
export PYTHONUTF8=1
PY=./venv/Scripts/python.exe
LOG="<スクラッチパッド>"

# 共通(月〜金)
$PY ats.py --media hrmos > "$LOG/hrmos.log" 2>&1; echo "HRMOS exit=$?"

# 火・木
$PY ats.py --media talentio > "$LOG/talentio.log" 2>&1; echo "Talentio exit=$?"

# 水・金
$PY ats.py --media jobcan > "$LOG/jobcan.log" 2>&1; echo "JobCan exit=$?"

# 月(リクナビの前に自動操作用ブラウザを確認。無ければ $PY -m playwright install chromium)
$PY rikunabi.py > "$LOG/rikunabi.log" 2>&1; echo "Rikunabi exit=$?"
(cd herp && ../venv/Scripts/python.exe herp.py) > "$LOG/herp.log" 2>&1; echo "HERP exit=$?"
```

## 4. 結果の確認

1. 各媒体の終了コードが 0 か確認する
2. ログを `grep -nE "❌|Error|失敗|Traceback"` で調べ、エラーが無いか確認する
3. 今日の日付のファイルがカテゴリ(WEB・IN_DS・CRS・CRG・コンサル)ごとに揃っているか、行数とあわせて確認する
   - HRMOS / Talentio / JobCan: `プログラム本体/output/{媒体}/{媒体}_{カテゴリ}_item_list_YYYY-MM-DD.csv`
   - リクナビ: `プログラム本体/output/rikunabi/rikunabi_{カテゴリ}_item_list_YYYYMMDD.csv`(`毎日の取得/output/rikunabi/` 側に出ることもある)
   - HERP: `プログラム本体/herp/output_herp_jobs/herp-{カテゴリ}-YYYYMMDD.csv`
4. 欠けている媒体・カテゴリや、行数が極端に少ない(ヘッダーのみ等)ファイルは「失敗」とみなす

### 失敗した媒体の再実行

- **1回目の再実行は確認不要**。失敗した媒体だけを、3 と同じコマンドでもう一度実行する(ログは `<媒体>_retry1.log` など別名にする)。
  終わったら、上の 1〜3 で同じように確認する
- **2回目以降の再実行は、必ずユーザーに確認してから**行う。ログの該当箇所を示して、再実行するか尋ねる
- 認証情報が無い・venv が無いなど、再実行しても直らないことが明らかな失敗は再実行せず、そのまま報告する

## 5. 報告

日本語で、次の内容を簡潔に伝えます。

- 実行した曜日と媒体、それぞれの成否(再実行した媒体は、その旨と再実行後の結果)
- 媒体 × カテゴリの表(行数はヘッダー込みと明記)
- 出力先フォルダ
- 「Drive へのアップロードはまだ済んでいない」こと(アップロードはユーザーが行う)

うまくいかない場合の連絡先はエンジニア(内山)です。
