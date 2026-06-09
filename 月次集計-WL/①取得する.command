#!/bin/bash
# 毎月1回(月初など)にダブルクリックするファイル その①
# 4つの媒体から求人データを自動で取ってきます(全部で30分〜2時間くらい)
cd "$(dirname "$0")" || exit 1
BASE="$PWD"
APP="$BASE/プログラム本体"

# 準備(はじめにこれ.command)で作ったPythonがあるか確認
PY="$APP/venv/bin/python"
if ! [ -x "$PY" ] || ! "$PY" -c "import playwright" >/dev/null 2>&1; then
  echo "準備がまだのようです。先に「はじめにこれ.command」をダブルクリックしてください。"
  echo "(実施済みの場合は、この画面のスクリーンショットを内山までお送りください)"
  exit 1
fi

ERRORS=""

run() {
  # run <表示名> <作業フォルダ> <スクリプト名>
  local name="$1" dir="$2" script="$3"
  echo ""
  echo "▶▶▶ ${name} を開始します..."
  echo "    (自動でブラウザが開きますが、操作せずにお待ちください)"
  if (cd "$dir" && "$PY" "$script"); then
    echo "◀◀◀ ${name} が終わりました"
  else
    echo "⚠️  ${name} でエラーが発生しました"
    ERRORS="${ERRORS} ${name}"
  fi
}

echo "=================================================="
echo " $(date +%Y年%m月%d日) 月次データ取得(その①)を始めます"
echo " 4つのサイトから順番にデータを取ります"
echo " 終わるまでこのウィンドウは閉じないでください"
echo " (全部で30分〜2時間くらいかかります)"
echo "=================================================="

run "atGP"               "$APP/atGP"               scrape_atgp.py
run "LITALICO仕事ナビ"    "$APP/LITALICO"           scrape_snabi_jobs.py
run "BABナビ"            "$APP/BABNAVI"            scraper.py
run "マイナビパートナーズ" "$APP/マイナビパートナーズ" scraper.py

echo ""
echo "=================================================="
if [ -n "$ERRORS" ]; then
  echo "⚠️ エラーが発生したもの:${ERRORS}"
  echo "   もう一度このファイルをダブルクリックしてください。"
  echo "   解消しない場合は、この画面のスクリーンショットを内山までお送りください。"
else
  echo " ✅ 4媒体のデータ取得が終わりました。"
fi
echo ""
echo " 次にやること(かんたん手順書.mdの「その②」):"
echo "  1. ブラウザで dodaチャレンジの検索結果ページを開く"
echo "  2. 「もっと見る」を表示されなくなるまで押す"
echo "  3. 求人一覧をコピーして「dodaここに貼る.txt」に貼って保存"
echo "  4. 「②集計する.command」をダブルクリック"
echo "=================================================="
echo ""
echo "このウィンドウは閉じて大丈夫です。"
