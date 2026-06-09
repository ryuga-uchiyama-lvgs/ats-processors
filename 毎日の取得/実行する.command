#!/bin/bash
# 毎日(平日)ダブルクリックするファイル。今日の曜日に合わせて自動で実行します。
cd "$(dirname "$0")" || exit 1
BASE="$PWD"

# 準備(はじめにこれ.command)で作ったPythonがあればそれを使う。なければパソコンのものを使う
PY="$BASE/プログラム本体/venv/bin/python"
[ -x "$PY" ] && "$PY" -c "import pandas" >/dev/null 2>&1 || PY="python3"
if ! "$PY" -c "import pandas, yaml, selenium, playwright" >/dev/null 2>&1; then
  echo "準備がまだのようです。先に「はじめにこれ.command」をダブルクリックしてください。"
  echo "(実施済みの場合は、この画面のスクリーンショットを内山までお送りください)"
  exit 1
fi

# テストモード(エンジニア確認用): 実際には実行せず、何が動くかだけ表示
PREFIX=""
[ "$1" = "--test" ] && PREFIX="echo [テスト・実際には動きません]"

DOW=$(date +%u)   # 1=月 ... 7=日
WDAYS=(月 火 水 木 金 土 日)
TODAY_LABEL="$(date +%Y年%m月%d日)(${WDAYS[$((DOW-1))]})"
ERRORS=""

# 月曜だけ使う「自動操作用ブラウザ」が入っているか確認し、無ければ自動で取得する。
# (Playwrightの更新後はブラウザを入れ直す必要があり、これが無いとリクナビ・HERPが失敗する)
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
  if (cd "$dir" && $PREFIX "$@"); then
    echo "◀◀◀ ${name} が終わりました"
  else
    echo "⚠️  ${name} でエラーが発生しました"
    ERRORS="${ERRORS} ${name}"
  fi
}

echo "=================================================="
echo " ${TODAY_LABEL} のデータ取得を始めます"
echo " 終わるまでこのウィンドウは閉じないでください"
echo " (リクナビ・HERPのある月曜は1時間以上かかります)"
echo "=================================================="

APP="$BASE/プログラム本体"
case "$DOW" in
  1) # 月曜: HRMOS + リクナビ + HERP
    run "HRMOS"    "$APP"      "$PY" ats.py --media hrmos
    ensure_browser   # リクナビ・HERPはブラウザが必要なので事前に確認
    run "リクナビ" "$APP"      "$PY" rikunabi.py
    run "HERP"     "$APP/herp" "$PY" herp.py
    ;;
  2|4) # 火・木: HRMOS + Talentio
    run "HRMOS"    "$APP" "$PY" ats.py --media hrmos
    run "Talentio" "$APP" "$PY" ats.py --media talentio
    ;;
  3|5) # 水・金: HRMOS + JobCan
    run "HRMOS"  "$APP" "$PY" ats.py --media hrmos
    run "JobCan" "$APP" "$PY" ats.py --media jobcan
    ;;
  *)
    echo "本日は土日のため、実行する処理はありません。"
    exit 0
    ;;
esac

echo ""
echo "=================================================="
echo " 本日作成されたファイル(Driveへアップロードしてください):"
echo "=================================================="
D1=$(date +%Y-%m-%d); D2=$(date +%Y%m%d)
FOUND=$(find -L output -type f \( -name "*${D1}*" -o -name "*${D2}*" \) 2>/dev/null)
if [ -n "$FOUND" ]; then
  echo "$FOUND" | sed 's/^/  ✅ /'
else
  echo "  ❌ 本日のファイルが見つかりません。もう一度実行してください。"
fi
if [ -n "$ERRORS" ]; then
  echo ""
  echo "⚠️ エラーが発生したもの:${ERRORS}"
  echo "   もう一度このファイルをダブルクリックしてください。"
  echo "   解消しない場合は、この画面のスクリーンショットを内山までお送りください。"
fi
echo ""
echo "このウィンドウは閉じて大丈夫です。"
