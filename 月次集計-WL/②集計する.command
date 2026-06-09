#!/bin/bash
# 毎月1回ダブルクリックするファイル その②
# ①とdodaの貼り付けが終わったあとに実行。重複を削除して納品用フォルダを作ります(数分)
cd "$(dirname "$0")" || exit 1
BASE="$PWD"
APP="$BASE/プログラム本体"
PASTE="$BASE/dodaここに貼る.txt"
TODAY=$(date +%Y%m%d)

# 準備(はじめにこれ.command)で作ったPythonがあるか確認
PY="$APP/venv/bin/python"
if ! [ -x "$PY" ]; then
  echo "準備がまだのようです。先に「はじめにこれ.command」をダブルクリックしてください。"
  exit 1
fi

fail() {
  echo ""
  echo "××××××××××××××××××××××××××××××××"
  echo " エラーが発生しました。"
  echo " この画面のスクリーンショットを撮って、"
  echo " 内山までお送りください。"
  echo "××××××××××××××××××××××××××××××××"
  exit 1
}

echo "=================================================="
echo " $(date +%Y年%m月%d日) 月次集計(その②)を始めます"
echo "=================================================="

# --- Step 1: dodaチャレンジの貼り付け内容をCSVに変換 ---
echo ""
echo "▶▶▶ [1/3] dodaチャレンジのデータを変換しています..."
if [ -f "$PASTE" ] && grep -q "<" "$PASTE"; then
  cp "$PASTE" "$APP/doda-challenge/doda-challenge.txt" || fail
  (cd "$APP/doda-challenge" && "$PY" parse_jobs.py) || fail
elif [ -n "$(find "$APP/doda-challenge/doda-jobs.csv" -newermt "$(date +%Y-%m-%d)" 2>/dev/null)" ]; then
  echo "(今日変換済みのdodaデータがあるので、それを使います)"
else
  echo ""
  echo "❌ 「dodaここに貼る.txt」にHTMLが貼られていないようです。"
  echo "   かんたん手順書.mdの「その②」を参照して、dodaチャレンジの"
  echo "   ページのHTMLを貼り付けてから、もう一度実行してください。"
  exit 1
fi

# --- Step 2: 5媒体まとめて正規化・重複削除 ---
echo ""
echo "▶▶▶ [2/3] 5媒体をまとめて集計しています..."
(cd "$APP" && "$PY" monthly_dedup.py "$TODAY") || fail

# --- Step 3: 納品用フォルダをこのフォルダに移動して検品 ---
echo ""
echo "▶▶▶ [3/3] できあがりを確認しています..."
OUT="$APP/${TODAY}_集計"
[ -d "$OUT" ] || fail
rm -rf "$BASE/${TODAY}_集計"
mv "$OUT" "$BASE/" || fail

COUNT=$(ls "$BASE/${TODAY}_集計" | wc -l | tr -d ' ')
echo ""
echo "=================================================="
echo " できたファイル(${TODAY}_集計 フォルダの中):"
ls "$BASE/${TODAY}_集計" | sed 's/^/  ✅ /'
if [ "$COUNT" -eq 7 ]; then
  echo ""
  echo " ✅ 7ファイルそろっています。"
  echo " 「${TODAY}_集計」フォルダを丸ごとGoogle Driveに"
  echo " アップロードしたら、今月の作業は完了です。"
  # 来月用に貼り付けファイルをリセット
  echo "(${TODAY} 集計済み) 来月、ここにdodaチャレンジのHTMLを貼り付けてください。貼り方は「かんたん手順書.md」の「その②」をご覧ください。" > "$PASTE"
else
  echo ""
  echo " ⚠️ ファイルが7個ありません(${COUNT}個)。"
  echo "   上に「[警告]」や「[SKIP]」が出ていたら、その媒体の"
  echo "   「①取得する.command」からやり直してください。"
  echo "   わからない場合は、この画面のスクリーンショットを内山までお送りください。"
fi
echo "=================================================="
echo ""
echo "このウィンドウは閉じて大丈夫です。"
