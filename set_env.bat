@echo off
REM Environment variables for Gambit Admin

set DATABASE_URL=postgresql://gambit_user:muneeb@localhost:5432/gambit_admin
set SESSION_SECRET=change_this_to_a_secure_random_string
set JWT_SECRET_KEY=change_this_to_a_secure_random_string
set FLASK_ENV=development

echo Environment variables set successfully!
