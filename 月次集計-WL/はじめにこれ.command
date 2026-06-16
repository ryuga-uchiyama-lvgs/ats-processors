#!/bin/bash
# 最初に1回だけダブルクリックするファイル(必要なプログラムを自動でインストールします)
cd "$(dirname "$0")" || exit 1

echo "=================================================="
echo " 準備を始めます(5〜10分くらいかかります)"
echo " 終わるまでこのウィンドウは閉じないでください"
echo "=================================================="
echo ""

fail() {
  echo ""
  echo "××××××××××××××××××××××××××××××××"
  echo " 準備中にエラーが発生しました。"
  echo " この画面のスクリーンショットを撮って、"
  echo " 内山までお送りください。"
  echo "××××××××××××××××××××××××××××××××"
  exit 1
}

# uv(実行環境を作る道具)を探す。よくある場所も見る。
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# 見つからなければ自動でインストールする(数十秒)
if ! command -v uv >/dev/null 2>&1; then
  echo "[1/4] 実行環境を作る道具(uv)をインストールしています..."
  curl -LsSf https://astral.sh/uv/install.sh | sh || fail
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 || fail

echo "[2/4] 実行環境を作成しています..."
# Python本体もuvが用意するので、パソコン側のPythonは不要です。
uv venv --clear --python 3.12 "プログラム本体/venv" || fail

echo "[3/4] 必要なプログラムを取得しています..."
uv pip install --python "プログラム本体/venv/bin/python" playwright || fail

echo "[4/4] 自動操作用のブラウザをインストールしています(いちばん時間がかかります)..."
"プログラム本体/venv/bin/python" -m playwright install chromium || fail

echo ""
echo "=================================================="
echo " ✅ 準備完了です。"
echo " 毎月の作業は"
echo "   「①取得する.command」→「②集計する.command」"
echo " の順に実行してください。"
echo " 詳しくは「かんたん手順書.md」をご覧ください。"
echo " このウィンドウは閉じて大丈夫です。"
echo "=================================================="
