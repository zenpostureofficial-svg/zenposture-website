@echo off
echo === ZenPosture GitHub Push ===
cd /d "%~dp0"
git init
git add .
git commit -m "Initial commit - ZenPosture website"
git branch -M main
git remote add origin https://github.com/zenpostureofficial-svg/zenposture-website.git
git push -u origin main
echo.
echo Done! Check https://github.com/zenpostureofficial-svg/zenposture-website
pause
