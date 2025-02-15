@echo off
cd /d "C:\clock"
del /F "*.png"
"C:\Users\Pharmacy\AppData\Local\Programs\Python\Python312\python.exe" "email_data_icndate.py"
pause