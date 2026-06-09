@echo off
chcp 65001 >nul
rem ============================================================
rem 毎月1回(月初など)にダブルクリックするファイル その①(Windows用)
rem 4つの媒体から求人データを自動で取ってきます(全部で30分～2時間くらい)
rem ============================================================
cd /d "%~dp0"
set PYTHONUTF8=1
set "PY=%~dp0プログラム本体\venv\Scripts\python.exe"
set "ERRORS="

rem --- 準備(はじめにこれ.bat)が終わっているか確認 ---
if not exist "%PY%" goto notready
"%PY%" -c "import playwright" >nul 2>&1
if errorlevel 1 goto notready

"%PY%" -c "import datetime;print(datetime.date.today().strftime('%%Y年%%m月%%d日'))" > "%TEMP%\ats_label.txt"
set /p TODAY_LABEL=<"%TEMP%\ats_label.txt"

echo ==================================================
echo  %TODAY_LABEL% 月次データ取得(その①)を始めます
echo  4つのサイトから順番にデータを取ります
echo  終わるまでこのウィンドウは閉じないでください
echo  (全部で30分～2時間くらいかかります)
echo ==================================================

call :run "atGP" "プログラム本体\atGP" scrape_atgp.py
call :run "LITALICO仕事ナビ" "プログラム本体\LITALICO" scrape_snabi_jobs.py
call :run "BABナビ" "プログラム本体\BABNAVI" scraper.py
call :run "マイナビパートナーズ" "プログラム本体\マイナビパートナーズ" scraper.py

echo.
echo ==================================================
if defined ERRORS goto haderrors
echo  [OK] 4媒体のデータ取得が終わりました。
goto nextsteps

:haderrors
echo [!] エラーが発生したもの:%ERRORS%
echo    もう一度このファイルをダブルクリックしてください。
echo    解消しない場合は、この画面のスクリーンショットを内山までお送りください。

:nextsteps
echo.
echo  次にやること(かんたん手順書.mdの「その②」):
echo   1. ブラウザで dodaチャレンジの検索結果ページを開く
echo   2. 「もっと見る」を表示されなくなるまで押す
echo   3. 求人一覧をコピーして「dodaここに貼る.txt」に貼って保存
echo   4. 「②集計する」(Windowsバッチファイル)をダブルクリック
echo ==================================================
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

:run
rem call :run <表示名> <作業フォルダ> <スクリプト名>
echo.
echo ▶▶▶ %~1 を開始します...
echo     (自動でブラウザが開きますが、操作せずにお待ちください)
pushd "%~2"
"%PY%" %3
if errorlevel 1 (
  echo [!] %~1 でエラーが発生しました
  set "ERRORS=%ERRORS% %~1"
) else (
  echo ◀◀◀ %~1 が終わりました
)
popd
exit /b 0
