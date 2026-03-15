@echo off
echo.
echo  ====================================
echo   Courtside Cre8ives - Data Refresh
echo  ====================================
echo.

cd /d %USERPROFILE%\heat-dashboard

echo  Pulling latest code...
git pull

echo.
echo  Fetching live NBA data (2-3 minutes)...
python scripts/refresh_data.py

echo.
echo  Pushing updated data to GitHub...
git add data/
git diff --cached --quiet
if %errorlevel%==0 (
    echo  Already up to date - no changes.
) else (
    git commit -m "data: refresh %date%"
    git push
    echo.
    echo  Done! App will update in ~1-2 minutes.
)

echo.
echo  All set!
echo.
pause
