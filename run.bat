@echo off
REM Activate the virtual environment
call .\venv\Scripts\activate.bat
REM Run the development server
python manage.py runserver
