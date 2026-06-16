@echo off
chcp 65001 >nul
rem ============================================================
rem 最初に1回だけダブルクリックするファイル(Windows用)
rem 必要なプログラムを自動でインストールします
rem (Pythonが未インストールの場合も自動でインストールします)
rem ============================================================
cd /d "%~dp0"
set PYTHONUTF8=1

echo ==================================================
echo  準備を始めます(5～15分くらいかかります)
echo  終わるまでこのウィンドウは閉じないでください
echo ==================================================
echo.

rem --- Pythonを探す(なければ自動インストール) ---
call :findpython
if defined PY_BOOT goto pyready

echo [0/4] Pythonが見つからないため、自動インストールします(数分かかります)...
set "PYINST=%TEMP%\python-installer.exe"
curl -L -s -o "%PYINST%" https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe
if errorlevel 1 goto nopython
"%PYINST%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1
if errorlevel 1 goto nopython
del /f /q "%PYINST%" >nul 2>&1
call :findpython
if not defined PY_BOOT goto nopython
echo       Pythonのインストールが完了しました。続けます...

:pyready
echo [1/4] 実行環境を作成しています...
%PY_BOOT% -m venv --clear "プログラム本体\venv"
if errorlevel 1 goto fail

echo [2/4] 必要なプログラムを取得しています(いちばん時間がかかります)...
"プログラム本体\venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
if errorlevel 1 goto fail
"プログラム本体\venv\Scripts\python.exe" -m pip install --quiet pandas pyyaml selenium webdriver-manager playwright
if errorlevel 1 goto fail

echo [3/4] 自動操作用のブラウザをインストールしています...
rem 社内ネットワーク(プロキシ/自己署名証明書)でダウンロードが弾かれる対策
set NODE_TLS_REJECT_UNAUTHORIZED=0
set PLAYWRIGHT_DOWNLOAD_HOST=
"プログラム本体\venv\Scripts\python.exe" -m playwright install chromium
if errorlevel 1 goto fail
set NODE_TLS_REJECT_UNAUTHORIZED=

echo [4/4] 保存先フォルダを設定しています...
rem Macで作った「ショートカット」はWindowsでは動かないため、ここで作り直す
if not exist "プログラム本体\herp\output_herp_jobs\" mkdir "プログラム本体\herp\output_herp_jobs"
if exist "プログラム本体\output" if not exist "プログラム本体\output\" del /f /q "プログラム本体\output"
if not exist "プログラム本体\output\" mklink /J "プログラム本体\output" "%~dp0output" >nul 2>&1
if exist "output\herp" if not exist "output\herp\" del /f /q "output\herp"
if not exist "output\herp\" mklink /J "output\herp" "%~dp0プログラム本体\herp\output_herp_jobs" >nul 2>&1

echo.
echo ==================================================
echo  [OK] 準備完了です。
echo  次回からは「実行する」(Windowsバッチファイル)の
echo  ダブルクリックのみで実行できます。
echo  このウィンドウは閉じて大丈夫です。
echo ==================================================
echo.
pause
exit /b 0

:findpython
rem Pythonを探してPY_BOOTに設定する(py → python → インストール先フォルダの順)
set "PY_BOOT="
py -3 --version >nul 2>&1
if not errorlevel 1 (
  set "PY_BOOT=py -3"
  exit /b 0
)
python --version >nul 2>&1
if not errorlevel 1 (
  set "PY_BOOT=python"
  exit /b 0
)
for /d %%d in ("%LocalAppData%\Programs\Python\Python3*") do if exist "%%d\python.exe" set "PY_BOOT="%%d\python.exe""
exit /b 0

:nopython
echo.
echo Pythonの自動インストールができませんでした。
echo 一番上のフォルダにある「Windowsで使うとき.md」の
echo 「初回の準備」に沿って手動でインストールしてから、
echo もう一度このファイルをダブルクリックしてください。
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
