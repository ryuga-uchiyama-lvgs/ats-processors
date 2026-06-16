@echo off
chcp 65001 >nul
rem ============================================================
rem 最初に1回だけダブルクリックするファイル(Windows用)
rem 必要なプログラムを自動でインストールします
rem (実行環境を作る道具 uv も、無ければ自動でインストールします)
rem ============================================================
cd /d "%~dp0"
set PYTHONUTF8=1

echo ==================================================
echo  準備を始めます(5～15分くらいかかります)
echo  終わるまでこのウィンドウは閉じないでください
echo ==================================================
echo.

rem --- uv(実行環境を作る道具)を探す。よくある場所もPATHに足す ---
set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"

where uv >nul 2>&1
if not errorlevel 1 goto uvready

echo [1/4] 実行環境を作る道具(uv)をインストールしています(数分かかります)...
powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"
if errorlevel 1 goto nouv
set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
where uv >nul 2>&1
if errorlevel 1 goto nouv
echo       uvのインストールが完了しました。続けます...

:uvready
echo [2/4] 実行環境を作成しています...
rem Python本体もuvが用意するので、パソコン側のPythonは不要です。
uv venv --clear --python 3.12 "プログラム本体\venv"
if errorlevel 1 goto fail

echo [3/4] 必要なプログラムを取得しています...
uv pip install --python "プログラム本体\venv\Scripts\python.exe" playwright
if errorlevel 1 goto fail

echo [4/4] 自動操作用のブラウザをインストールしています(いちばん時間がかかります)...
rem 社内ネットワーク(プロキシ/自己署名証明書)でダウンロードが弾かれる対策
set NODE_TLS_REJECT_UNAUTHORIZED=0
"プログラム本体\venv\Scripts\python.exe" -m playwright install chromium
if errorlevel 1 goto fail
set NODE_TLS_REJECT_UNAUTHORIZED=

echo.
echo ==================================================
echo  [OK] 準備完了です。
echo  毎月の作業は
echo    「①取得する」→「②集計する」(Windowsバッチファイル)
echo  の順に実行してください。
echo  詳しくは「かんたん手順書.md」をご覧ください。
echo  このウィンドウは閉じて大丈夫です。
echo ==================================================
echo.
pause
exit /b 0

:nouv
echo.
echo 実行環境を作る道具(uv)のインストールができませんでした。
echo インターネット接続を確認して、もう一度このファイルを
echo ダブルクリックしてください。
echo 解消しない場合は、この画面のスクリーンショットを撮って
echo 内山までお送りください。
echo.
pause
exit /b 1

:fail
echo.
echo ××××××××××××××××××××××××××××××××
echo  準備中にエラーが発生しました。
echo  この画面のスクリーンショットを撮って、
echo  内山までお送りください。
echo ××××××××××××××××××××××××××××××××
echo.
pause
exit /b 1
