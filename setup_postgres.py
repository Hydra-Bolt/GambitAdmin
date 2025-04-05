"""
PostgreSQL Database Setup Script for Gambit Admin

This script guides you through setting up a PostgreSQL database for the Gambit Admin project.
It will:
1. Check if PostgreSQL is installed
2. Help you create a database and user
3. Set up environment variables

Note: You need to have PostgreSQL installed before running this script.
"""

import os
import subprocess
import sys
import platform
import getpass
import psycopg2
from psycopg2 import sql

# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

def print_colored(text, color):
    """Print colored text to the terminal"""
    print(f"{color}{text}{Colors.END}")

def print_header(text):
    """Print a header with formatting"""
    print("\n" + "=" * 80)
    print_colored(text, Colors.BOLD + Colors.BLUE)
    print("=" * 80 + "\n")

def print_step(text):
    """Print a step with formatting"""
    print_colored(f"➤ {text}", Colors.BOLD + Colors.GREEN)

def print_warning(text):
    """Print a warning with formatting"""
    print_colored(f"⚠️  {text}", Colors.BOLD + Colors.YELLOW)

def print_error(text):
    """Print an error with formatting"""
    print_colored(f"❌ {text}", Colors.BOLD + Colors.RED)

def run_command(command, shell=True):
    """Run a command and return its output"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=True, 
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        return None

def find_postgres_bin_dir():
    """Find PostgreSQL binary directory on Windows"""
    possible_paths = []
    
    # Check Program Files
    for root_dir in ["C:\\Program Files\\PostgreSQL", "C:\\Program Files (x86)\\PostgreSQL"]:
        if os.path.isdir(root_dir):
            # Get all version directories
            version_dirs = [os.path.join(root_dir, d) for d in os.listdir(root_dir) 
                          if os.path.isdir(os.path.join(root_dir, d))]
            
            # Add bin directory for each version
            for ver_dir in version_dirs:
                bin_dir = os.path.join(ver_dir, "bin")
                if os.path.isdir(bin_dir) and os.path.exists(os.path.join(bin_dir, "psql.exe")):
                    possible_paths.append(bin_dir)
    
    # Check for additional common installation paths
    additional_paths = [
        "C:\\PostgreSQL\\bin",
        os.path.expanduser("~\\AppData\\Local\\Programs\\PostgreSQL\\bin"),
        os.path.expanduser("~\\scoop\\apps\\postgresql\\current\\bin")
    ]
    
    for path in additional_paths:
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "psql.exe")):
            possible_paths.append(path)
            
    return possible_paths

def check_postgres_installed():
    """Check if PostgreSQL is installed"""
    print_step("Checking if PostgreSQL is installed...")
    
    if platform.system() == "Windows":
        # Find PostgreSQL bin directory
        postgres_bin_dirs = find_postgres_bin_dir()
        
        if postgres_bin_dirs:
            print_colored(f"Found PostgreSQL installations in: {', '.join(postgres_bin_dirs)}", Colors.GREEN)
            
            # Check if any of the bin directories are in PATH
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            in_path = any(bin_dir.lower() in [p.lower() for p in path_dirs] for bin_dir in postgres_bin_dirs)
            
            if not in_path:
                print_warning("PostgreSQL bin directory is not in your PATH environment variable.")
                print_warning(f"Using first found PostgreSQL installation: {postgres_bin_dirs[0]}")
            
            os.environ['PG_BIN_DIR'] = postgres_bin_dirs[0]
            return True
        else:
            print_error("PostgreSQL installation not found in Program Files.")
            return False
    else:
        # For Unix-like systems
        try:
            version = run_command("psql --version")
            if version:
                print_colored(f"Found PostgreSQL: {version}", Colors.GREEN)
                return True
        except:
            pass
    
    print_error("PostgreSQL is not installed or not in PATH.")
    return False

def install_postgres_guide():
    """Guide for installing PostgreSQL"""
    print_header("PostgreSQL Installation Guide")
    print("You need to install PostgreSQL before continuing.")
    
    if platform.system() == "Windows":
        print("""
1. Download the installer from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the instructions.
3. Remember the password you set for the 'postgres' user!
4. During installation, use the default port (5432).
5. After installation, add the PostgreSQL bin directory to your PATH.
   (Typically: C:\\Program Files\\PostgreSQL\\<version>\\bin)
6. Restart your terminal/computer.
7. Run this script again.
""")
        
        # Additional guidance if PostgreSQL may be installed but not in PATH
        postgres_bin_dirs = find_postgres_bin_dir()
        if postgres_bin_dirs:
            print_warning("PostgreSQL seems to be installed but the bin directory is not in your PATH.")
            print("You have two options:")
            print(f"1. Add {postgres_bin_dirs[0]} to your PATH environment variable")
            print("2. Temporarily set the PATH for this session using the following command:")
            print(f"   set PATH=%PATH%;{postgres_bin_dirs[0]}")
            print("   Then run this script again.")
    
    elif platform.system() == "Darwin":  # macOS
        print("""
1. Install PostgreSQL using Homebrew: 
   brew install postgresql
2. Start PostgreSQL service:
   brew services start postgresql
3. Run this script again.
""")
    else:  # Linux
        print("""
1. Install PostgreSQL using your package manager:
   For Ubuntu/Debian: sudo apt update && sudo apt install postgresql postgresql-contrib
   For Fedora/RHEL:   sudo dnf install postgresql postgresql-server
2. Start PostgreSQL service:
   sudo systemctl start postgresql
3. Run this script again.
""")
    
    sys.exit(1)

def get_database_config():
    """Get database configuration from user input"""
    print_header("Database Configuration")
    print("Please enter the following information to set up your database:")
    
    # Default values
    config = {
        "db_name": "gambit_admin",
        "db_user": "gambit_user",
        "db_password": "",
        "db_host": "localhost",
        "db_port": "5432"
    }
    
    config["db_name"] = input(f"Database name [{config['db_name']}]: ") or config["db_name"]
    config["db_user"] = input(f"Database user [{config['db_user']}]: ") or config["db_user"]
    config["db_password"] = getpass.getpass(f"Database password: ")
    config["db_host"] = input(f"Database host [{config['db_host']}]: ") or config["db_host"]
    config["db_port"] = input(f"Database port [{config['db_port']}]: ") or config["db_port"]
    
    return config

def create_postgres_db(config):
    """Create PostgreSQL database and user"""
    print_header("Creating PostgreSQL Database")
    
    print_step("Creating database and user...")
    
    # SQL commands to create user and database
    sql_commands = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '{config['db_user']}') THEN
            CREATE USER {config['db_user']} WITH PASSWORD '{config['db_password']}';
        END IF;
    END
    $$;

    CREATE DATABASE {config['db_name']};
    GRANT ALL PRIVILEGES ON DATABASE {config['db_name']} TO {config['db_user']};
    """
    
    # Write SQL to a temporary file
    temp_sql_file = "temp_db_setup.sql"
    with open(temp_sql_file, "w") as f:
        f.write(sql_commands)
    
    # Run the SQL commands as the postgres user
    try:
        if platform.system() == "Windows":
            # On Windows, use the psql command directly
            print_warning("You may be prompted for the password of the 'postgres' user.")
            
            # Get the PostgreSQL bin directory
            psql_path = "psql"
            if 'PG_BIN_DIR' in os.environ:
                psql_path = os.path.join(os.environ['PG_BIN_DIR'], "psql")
                
            cmd = f'"{psql_path}" -U postgres -f {temp_sql_file}'
            print_colored(f"Running command: {cmd}", Colors.BLUE)
            
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                text=True
            )
        else:
            # On Unix-like systems, use sudo to switch to the postgres user
            print_warning("You may be prompted for your sudo password.")
            result = subprocess.run(
                f'sudo -u postgres psql -f {temp_sql_file}',
                shell=True,
                check=True,
                text=True
            )
        
        print_colored("Database and user created successfully!", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create database: {e}")
        
        if platform.system() == "Windows":
            # Give additional guidance
            print_warning("This could be due to PostgreSQL binaries not being in your PATH.")
            postgres_bin_dirs = find_postgres_bin_dir()
            if postgres_bin_dirs:
                print_colored("Try running the following commands:", Colors.YELLOW)
                bin_dir = postgres_bin_dirs[0]
                print(f"1. set PATH=%PATH%;{bin_dir}")
                print(f"2. Run this script again")
            else:
                print_warning("Make sure PostgreSQL is installed correctly.")
        
        return False
    finally:
        # Remove the temporary SQL file
        if os.path.exists(temp_sql_file):
            os.remove(temp_sql_file)

def create_env_file(config):
    """Create .env file with database configuration"""
    print_header("Creating Environment File")
    
    # Create the DATABASE_URL
    db_url = f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
    
    # Content of .env file
    env_content = f"""# Database configuration
DATABASE_URL={db_url}

# Secret keys
SESSION_SECRET=change_this_to_a_secure_random_string
JWT_SECRET_KEY=change_this_to_a_secure_random_string

# Flask environment
FLASK_ENV=development
"""
    
    # Write to .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print_colored(".env file created successfully!", Colors.GREEN)
    print_warning("Note: You should change the secret keys to secure random strings in production.")
    
    return db_url

def create_env_bat(db_url):
    """Create set_env.bat for Windows users"""
    bat_content = f"""@echo off
REM Environment variables for Gambit Admin

set DATABASE_URL={db_url}
set SESSION_SECRET=change_this_to_a_secure_random_string
set JWT_SECRET_KEY=change_this_to_a_secure_random_string
set FLASK_ENV=development

echo Environment variables set successfully!
"""
    
    with open("set_env.bat", "w") as f:
        f.write(bat_content)
    
    print_colored("set_env.bat file created for Windows users.", Colors.GREEN)

def create_env_sh(db_url):
    """Create set_env.sh for Unix users"""
    sh_content = f"""#!/bin/bash
# Environment variables for Gambit Admin

export DATABASE_URL="{db_url}"
export SESSION_SECRET="change_this_to_a_secure_random_string"
export JWT_SECRET_KEY="change_this_to_a_secure_random_string"
export FLASK_ENV="development"

echo "Environment variables set successfully!"
"""
    
    with open("set_env.sh", "w") as f:
        f.write(sh_content)
    
    # Make the file executable
    os.chmod("set_env.sh", 0o755)
    
    print_colored("set_env.sh file created for Unix users.", Colors.GREEN)

def setup_database():
    """Grant privileges to the user on the public schema"""
    db_name = "gambit_admin"
    db_user = "gambit_user"
    db_password = "muneeb"  # Replace with the actual password
    db_host = "localhost"  # Update if hosted elsewhere
    db_port = "5432"  # Default PostgreSQL port

    try:
        # Connect to the PostgreSQL server as a superuser
        conn = psycopg2.connect(
            dbname="postgres", user="postgres", password="muneeb", host=db_host, port=db_port
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Grant privileges to the user
        cursor.execute(sql.SQL(
            """
            GRANT ALL PRIVILEGES ON SCHEMA public TO {user};
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {user};
            """
        ).format(user=sql.Identifier(db_user)))

        print(f"Privileges granted to user '{db_user}' on schema 'public'.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()

def main():
    """Main function to run the setup script"""
    print_header("Gambit Admin PostgreSQL Setup")
    
    # Check if PostgreSQL is installed
    if not check_postgres_installed():
        install_postgres_guide()
    
    # Get database configuration
    config = get_database_config()
    
    # Create database and user
    if create_postgres_db(config):
        # Grant privileges to the user
        setup_database()
        
        # Create environment files
        db_url = create_env_file(config)
        
        # Create platform-specific environment scripts
        create_env_bat(db_url)
        create_env_sh(db_url)
        
        print_header("Setup Complete")
        print("""
Your PostgreSQL database is set up and ready to use with Gambit Admin!

To set the environment variables:
- On Windows: Run set_env.bat
- On Unix/Mac: Run source set_env.sh

Then run your application:
- python main.py

This will initialize the database tables and populate them with sample data.
""")
    else:
        print_error("Database setup failed. Please check the error messages and try again.")

if __name__ == "__main__":
    main()