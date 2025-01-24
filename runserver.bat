@echo off

:: Navigate to the project directory
cd /d C:\Users\Admin\Desktop\testings_vms\vms_tanzania

:: Activate the virtual environment
call myvenv\Scripts\activate.bat

:: Verify the virtual environment activation
if not defined VIRTUAL_ENV (
    echo Virtual environment activation failed.
    pause
    exit /b 1
)

:: Navigate to the Django project directory
cd /d C:\Users\Admin\Desktop\testings_vms\vms_tanzania

:: Run the Django server with SSL certificates
C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe manage.py runserver_plus --cert-file selfsigned.crt --key-file selfsigned.key 192.168.1.137:7000