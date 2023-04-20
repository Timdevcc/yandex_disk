pyinstaller --onefile main.py
move dist\main.exe
del main.spec
rd dist build /Q /S