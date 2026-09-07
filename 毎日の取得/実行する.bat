@echo off
chcp 65001 >nul
rem ============================================================
rem 毎日(平日)ダブルクリックするファイル(Windows用)
rem 今日の曜日に合わせて自動で実行します
rem ============================================================
cd /d "%~dp0"
set PYTHONUTF8=1
set "PY=%~dp0プログラム本体\venv\Scripts\python.exe"
set "ERRORS="

rem --- 準備(はじめにこれ.bat)が終わっているか確認 ---
if not exist "%PY%" goto notready
"%PY%" -c "import pandas, yaml, selenium, playwright" >nul 2>&1
if errorlevel 1 goto notready

rem --- 今日の曜日と日付ラベルを取得 ---
"%PY%" -c "import datetime;print(datetime.date.today().isoweekday())" > "%TEMP%\ats_dow.txt"
set /p DOW=<"%TEMP%\ats_dow.txt"
"%PY%" -c "import datetime;d=datetime.date.today();print(d.strftime('%%Y年%%m月%%d日')+'('+'月火水木金土日'[d.isoweekday()-1]+')')" > "%TEMP%\ats_label.txt"
set /p TODAY_LABEL=<"%TEMP%\ats_label.txt"

echo ==================================================
echo  %TODAY_LABEL% のデータ取得を始めます
echo  終わるまでこのウィンドウは閉じないでください
echo  (リクナビ・HERPのある月曜は1時間以上かかります)
echo ==================================================

if "%DOW%"=="1" goto mon
if "%DOW%"=="2" goto tue_thu
if "%DOW%"=="4" goto tue_thu
if "%DOW%"=="3" goto wed_fri
if "%DOW%"=="5" goto wed_fri
goto weekend

:mon
call :run "HRMOS" "プログラム本体" ats.py --media hrmos
call :ensure_browser
call :run "リクナビ" "プログラム本体" rikunabi.py
call :check_herp_ready
if errorlevel 1 (
  set "ERRORS=%ERRORS% HERP"
) else (
  call :run "HERP" "プログラム本体\herp" herp.py
)
goto summary

:tue_thu
call :run "HRMOS" "プログラム本体" ats.py --media hrmos
call :run "Talentio" "プログラム本体" ats.py --media talentio
goto summary

:wed_fri
call :run "HRMOS" "プログラム本体" ats.py --media hrmos
call :run "JobCan" "プログラム本体" ats.py --media jobcan
goto summary

:weekend
echo.
echo 本日は土日のため、実行する処理はありません。
echo.
pause
exit /b 0

:summary
echo.
echo ==================================================
echo  本日作成されたファイル(Driveへアップロードしてください):
echo ==================================================
"%PY%" -c "import datetime,glob,os;d1=datetime.date.today().strftime('%%Y-%%m-%%d');d2=d1.replace('-','');ps=[p for r in ['output','プログラム本体/output','プログラム本体/herp/output_herp_jobs'] for p in glob.glob(r+'/**/*',recursive=True) if os.path.isfile(p) and (d1 in os.path.basename(p) or d2 in os.path.basename(p))];seen=set();ps=[p for p in ps if not (os.path.realpath(p) in seen or seen.add(os.path.realpath(p)))];print('\n'.join('  [OK] '+p for p in ps) if ps else '  [X] 本日のファイルが見つかりません。もう一度実行してください。')"
if defined ERRORS goto haderrors
echo.
echo このウィンドウは閉じて大丈夫です。
echo.
pause
exit /b 0

:haderrors
echo.
echo [!] エラーが発生したもの:%ERRORS%
echo    もう一度このファイルをダブルクリックしてください。
echo    解消しない場合は、この画面のスクリーンショットを内山までお送りください。
echo.
pause
exit /b 1

:notready
echo 準備がまだのようです。先に「はじめにこれ」(Windowsバッチファイル)をダブルクリックしてください。
echo (実施済みの場合は、この画面のスクリーンショットを内山までお送りください)
echo.
pause
exit /b 1

:check_herp_ready
rem HERPはログインが必要(2026/8/5〜)。ID/PASSはHRMOS等と同じ config.yaml を読む(2026/9/4〜)
if exist "プログラム本体\config.yaml" exit /b 0
echo.
echo [!] HERPをスキップします: プログラム本体\config.yaml が見つかりません
echo    HERPはログインが必要なため、このファイルが無いと取得できません。(HRMOS等と同じファイルです)
echo    config.yaml を配置してから、もう一度実行してください。(入手方法は内山まで)
exit /b 1

:ensure_browser
rem 月曜だけ使う「自動操作用ブラウザ」が入っているか確認し、無ければ自動で取得する
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
  set "ERRORS=%ERRORS% %~1"
) else (
  echo ◀◀◀ %~1 が終わりました
)
popd
exit /b 0
