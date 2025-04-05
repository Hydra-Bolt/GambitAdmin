#!/bin/bash
# Environment variables for Gambit Admin

export DATABASE_URL="postgresql://gambit_user:muneeb@localhost:5432/gambit_admin"
export SESSION_SECRET="change_this_to_a_secure_random_string"
export JWT_SECRET_KEY="change_this_to_a_secure_random_string"
export FLASK_ENV="development"

echo "Environment variables set successfully!"
