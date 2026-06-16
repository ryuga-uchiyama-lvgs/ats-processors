@echo off
chcp 65001 >nul
rem ============================================================
rem 媒体を1つ選んで単発で実行するファイル(Windows用)
rem (曜日に関係なく、好きな媒体だけを動かしたいときに使います)
rem ============================================================
cd /d "%~dp0"
set PYTHONUTF8=1
set "PY=%~dp0プログラム本体\venv\Scripts\python.exe"

rem --- 準備(はじめにこれ.bat)が終わっているか確認 ---
if not exist "%PY%" goto notready
"%PY%" -c "import pandas, yaml, selenium, playwright" >nul 2>&1
if errorlevel 1 goto notready

:menu
echo ==================================================
echo  実行したい媒体の番号を入力して Enter を押してください
echo ==================================================
echo   1) HRMOS
echo   2) Talentio
echo   3) JobCan
echo   4) リクナビ（全カテゴリ）
echo   5) リクナビ（カテゴリを指定）
echo   6) HERP
echo   q) やめる
echo --------------------------------------------------
set "choice="
set /p "choice=番号: "

if "%choice%"=="1" call :run "HRMOS" "プログラム本体" ats.py --media hrmos & goto summary
if "%choice%"=="2" call :run "Talentio" "プログラム本体" ats.py --media talentio & goto summary
if "%choice%"=="3" call :run "JobCan" "プログラム本体" ats.py --media jobcan & goto summary
if "%choice%"=="4" (call :ensure_browser & call :run "リクナビ（全カテゴリ）" "プログラム本体" rikunabi.py & goto summary)
if "%choice%"=="5" goto rikunabi_cat
if "%choice%"=="6" (call :ensure_browser & call :run "HERP" "プログラム本体\herp" herp.py & goto summary)
if /i "%choice%"=="q" echo 中止しました。& exit /b 0
echo 1〜6 または q を入力してください。
echo.
goto menu

:rikunabi_cat
echo.
echo カテゴリ名を入力してください（例: WEB / IN_DS / CRS / CRG / コンサル）
set "cat="
set /p "cat=カテゴリ名: "
if "%cat%"=="" echo カテゴリ名が空のため中止しました。& exit /b 1
call :ensure_browser
call :run "リクナビ（%cat%）" "プログラム本体" rikunabi.py "%cat%"
goto summary

:summary
echo.
echo ==================================================
echo  作成されたファイル(Driveへアップロードしてください):
echo ==================================================
"%PY%" -c "import datetime,glob,os;d1=datetime.date.today().strftime('%%Y-%%m-%%d');d2=d1.replace('-','');ps=[p for r in ['output','プログラム本体/output','プログラム本体/herp/output_herp_jobs'] for p in glob.glob(r+'/**/*',recursive=True) if os.path.isfile(p) and (d1 in os.path.basename(p) or d2 in os.path.basename(p))];seen=set();ps=[p for p in ps if not (os.path.realpath(p) in seen or seen.add(os.path.realpath(p)))];print('\n'.join('  [OK] '+p for p in ps) if ps else '  （本日付のファイルは見つかりませんでした）')"
echo.
echo このウィンドウは閉じて大丈夫です。
echo.
pause
exit /b 0

:notready
echo 準備がまだのようです。先に「はじめにこれ」(Windowsバッチファイル)をダブルクリックしてください。
echo (実施済みの場合は、この画面のスクリーンショットを内山までお送りください)
echo.
pause
exit /b 1

:ensure_browser
rem 自動操作用ブラウザ(リクナビ・HERPで使用)が入っているか確認し、無ければ取得する
"%PY%" -c "import os,sys;from playwright.sync_api import sync_playwright;p=sync_playwright().start();ok=os.path.exists(p.chromium.executable_path);p.stop();sys.exit(0 if ok else 1)" >nul 2>&1
if not errorlevel 1 exit /b 0
echo     (自動操作用のブラウザを取得します。数分かかります。お待ちください...)
"%PY%" -m playwright install chromium
exit /b 0

:run
rem call :run <表示名> <作業フォルダ> <スクリプト名> [引数...]
echo.
echo ▶▶▶ %~1 を開始します...
echo     (自動でブラウザが開きますが、操作せずにお待ちください)
pushd "%~2"
"%PY%" %3 %4 %5
if errorlevel 1 (
  echo [!] %~1 でエラーが発生しました
  echo    もう一度実行しても解消しない場合は、この画面のスクリーンショットを内山までお送りください。
) else (
  echo ◀◀◀ %~1 が終わりました
)
popd
exit /b 0
