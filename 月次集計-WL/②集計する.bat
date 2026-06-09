@echo off
chcp 65001 >nul
rem ============================================================
rem 毎月1回ダブルクリックするファイル その②(Windows用)
rem ①とdodaの貼り付けが終わったあとに実行。
rem 重複を削除して納品用フォルダを作ります(数分)
rem ============================================================
cd /d "%~dp0"
set PYTHONUTF8=1
set "PY=%~dp0プログラム本体\venv\Scripts\python.exe"

rem --- 準備(はじめにこれ.bat)が終わっているか確認 ---
if not exist "%PY%" goto notready

"%PY%" -c "import datetime;print(datetime.date.today().strftime('%%Y%%m%%d'))" > "%TEMP%\ats_today.txt"
set /p TODAY=<"%TEMP%\ats_today.txt"
"%PY%" -c "import datetime;print(datetime.date.today().strftime('%%Y年%%m月%%d日'))" > "%TEMP%\ats_label.txt"
set /p TODAY_LABEL=<"%TEMP%\ats_label.txt"

echo ==================================================
echo  %TODAY_LABEL% 月次集計(その②)を始めます
echo ==================================================

rem --- Step 1: dodaチャレンジの貼り付け内容をCSVに変換 ---
echo.
echo ▶▶▶ [1/3] dodaチャレンジのデータを変換しています...
findstr /c:"<" "dodaここに貼る.txt" >nul 2>&1
if errorlevel 1 goto checkdone
copy /y "dodaここに貼る.txt" "プログラム本体\doda-challenge\doda-challenge.txt" >nul
if errorlevel 1 goto fail
pushd "プログラム本体\doda-challenge"
"%PY%" parse_jobs.py
if errorlevel 1 goto failpop
popd
goto step2

:checkdone
rem 貼り付けがなくても、今日変換済みのdodaデータがあればそれを使う
"%PY%" -c "import os,sys,datetime;p='プログラム本体/doda-challenge/doda-jobs.csv';sys.exit(0 if os.path.exists(p) and datetime.date.fromtimestamp(os.path.getmtime(p))==datetime.date.today() else 1)"
if errorlevel 1 goto nododa
echo (今日変換済みのdodaデータがあるので、それを使います)
goto step2

:nododa
echo.
echo [X] 「dodaここに貼る.txt」にHTMLが貼られていないようです。
echo    かんたん手順書.mdの「その②」を参照して、dodaチャレンジの
echo    ページのHTMLを貼り付けてから、もう一度実行してください。
echo.
pause
exit /b 1

rem --- Step 2: 5媒体まとめて正規化・重複削除 ---
:step2
echo.
echo ▶▶▶ [2/3] 5媒体をまとめて集計しています...
pushd "プログラム本体"
"%PY%" monthly_dedup.py %TODAY%
if errorlevel 1 goto failpop
popd

rem --- Step 3: 納品用フォルダをこのフォルダに移動して検品 ---
echo.
echo ▶▶▶ [3/3] できあがりを確認しています...
if not exist "プログラム本体\%TODAY%_集計\" goto fail
if exist "%TODAY%_集計\" rd /s /q "%TODAY%_集計"
move "プログラム本体\%TODAY%_集計" . >nul
if errorlevel 1 goto fail

set COUNT=0
for %%f in ("%TODAY%_集計\*") do set /a COUNT+=1

echo.
echo ==================================================
echo  できたファイル(%TODAY%_集計 フォルダの中):
for %%f in ("%TODAY%_集計\*") do echo   [OK] %%~nxf
if "%COUNT%"=="7" goto ok7
echo.
echo  [!] ファイルが7個ありません(%COUNT%個^)。
echo    上に「[警告]」や「[SKIP]」が出ていたら、その媒体の
echo    「①取得する」からやり直してください。
echo    わからない場合は、この画面のスクリーンショットを内山までお送りください。
goto end

:ok7
echo.
echo  [OK] 7ファイルそろっています。
echo  「%TODAY%_集計」フォルダを丸ごとGoogle Driveに
echo  アップロードしたら、今月の作業は完了です。
rem 来月用に貼り付けファイルをリセット
>"dodaここに貼る.txt" echo (%TODAY% 集計済み^) 来月、ここにdodaチャレンジのHTMLを貼り付けてください。貼り方は「かんたん手順書.md」の「その②」をご覧ください。

:end
echo ==================================================
echo.
echo このウィンドウは閉じて大丈夫です。
echo.
pause
exit /b 0

:notready
echo 準備がまだのようです。先に「はじめにこれ」(Windowsバッチファイル)をダブルクリックしてください。
echo.
pause
exit /b 1

:failpop
popd

:fail
echo.
echo ××××××××××××××××××××××××××××××××
echo  エラーが発生しました。
echo  この画面のスクリーンショットを撮って、
echo  内山までお送りください。
echo ××××××××××××××××××××××××××××××××
echo.
pause
exit /b 1
