@echo off
echo Cleaning Python cache files...
del /s /q *.pyc
rmdir /s /q __pycache__
rmdir /s /q cogs\__pycache__
rmdir /s /q database\__pycache__
rmdir /s /q utils\__pycache__
echo Done! Cache cleaned.
echo Now run: python bot.py
pause
