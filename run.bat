@echo off
start py manage.py runserver
timeout /t 3
start http://127.0.0.1:8000/
