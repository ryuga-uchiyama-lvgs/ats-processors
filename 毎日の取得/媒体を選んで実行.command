#!/bin/bash
# 媒体を1つ選んで単発で実行するファイル。
# (曜日に関係なく、好きな媒体だけを動かしたいときに使います)
cd "$(dirname "$0")" || exit 1
BASE="$PWD"

# 準備(はじめにこれ)で作ったPythonがあればそれを使う。なければパソコンのものを使う
PY="$BASE/プログラム本体/venv/bin/python"
[ -x "$PY" ] && "$PY" -c "import pandas" >/dev/null 2>&1 || PY="python3"
if ! "$PY" -c "import pandas, yaml, selenium, playwright" >/dev/null 2>&1; then
  echo "準備がまだのようです。先に「はじめにこれ.command」をダブルクリックしてください。"
  echo "(実施済みの場合は、この画面のスクリーンショットを内山までお送りください)"
  exit 1
fi

APP="$BASE/プログラム本体"

# 自動操作用ブラウザ(リクナビ・HERPで使用)が入っているか確認し、無ければ取得する
ensure_browser() {
  if "$PY" -c "import os,sys;from playwright.sync_api import sync_playwright;p=sync_playwright().start();ok=os.path.exists(p.chromium.executable_path);p.stop();sys.exit(0 if ok else 1)" >/dev/null 2>&1; then
    return 0
  fi
  echo "    (自動操作用のブラウザを取得します。数分かかります。お待ちください...)"
  "$PY" -m playwright install chromium
}

run() {
  # run <表示名> <作業フォルダ> <コマンド...>
  local name="$1" dir="$2"; shift 2
  echo ""
  echo "▶▶▶ ${name} を開始します..."
  echo "    (自動でブラウザが開きますが、操作せずにお待ちください)"
  if (cd "$dir" && "$@"); then
    echo "◀◀◀ ${name} が終わりました"
  else
    echo "⚠️  ${name} でエラーが発生しました"
    echo "   もう一度実行しても解消しない場合は、この画面のスクリーンショットを内山までお送りください。"
  fi
}

echo "=================================================="
echo " 実行したい媒体の番号を入力して Enter を押してください"
echo "=================================================="
echo "  1) HRMOS"
echo "  2) Talentio"
echo "  3) JobCan"
echo "  4) リクナビ（全カテゴリ）"
echo "  5) リクナビ（カテゴリを指定）"
echo "  6) HERP"
echo "  q) やめる"
echo "--------------------------------------------------"
read -r -p "番号: " choice

case "$choice" in
  1) run "HRMOS"    "$APP" "$PY" ats.py --media hrmos ;;
  2) run "Talentio" "$APP" "$PY" ats.py --media talentio ;;
  3) run "JobCan"   "$APP" "$PY" ats.py --media jobcan ;;
  4) ensure_browser; run "リクナビ（全カテゴリ）" "$APP" "$PY" rikunabi.py ;;
  5)
     echo ""
     echo "カテゴリ名を入力してください（例: WEB / IN_DS / CRS / CRG / コンサル）"
     read -r -p "カテゴリ名: " cat
     if [ -z "$cat" ]; then
       echo "カテゴリ名が空のため中止しました。"
       exit 1
     fi
     ensure_browser
     run "リクナビ（${cat}）" "$APP" "$PY" rikunabi.py "$cat"
     ;;
  6) ensure_browser; run "HERP" "$APP/herp" "$PY" herp.py ;;
  q|Q) echo "中止しました。"; exit 0 ;;
  *) echo "1〜6 または q を入力してください。"; exit 1 ;;
esac

echo ""
echo "=================================================="
echo " 作成されたファイル(Driveへアップロードしてください):"
echo "=================================================="
D1=$(date +%Y-%m-%d); D2=$(date +%Y%m%d)
FOUND=$(find -L output "プログラム本体/herp/output_herp_jobs" -type f \( -name "*${D1}*" -o -name "*${D2}*" \) 2>/dev/null)
if [ -n "$FOUND" ]; then
  echo "$FOUND" | sed 's/^/  ✅ /'
else
  echo "  （本日付のファイルは見つかりませんでした）"
fi
echo ""
echo "このウィンドウは閉じて大丈夫です。"
