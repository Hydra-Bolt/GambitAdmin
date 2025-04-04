import os
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Setup database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT configuration
# Use a simple fixed key for development
app.config["JWT_SECRET_KEY"] = "dev-key-123456"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # 1 hour
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)  # 30 days
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize Flask-JWT-Extended
jwt = JWTManager(app)
from utils.auth import register_jwt_error_handlers
register_jwt_error_handlers(jwt)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import AdminModel
    return AdminModel.query.get(int(user_id))

# Import and register routes
from routes.subscribers import subscribers_bp
from routes.users import users_bp
from routes.leagues import leagues_bp
from routes.teams import teams_bp
from routes.dashboard import dashboard_bp
from routes.players import players_bp
from routes.reels import reels_bp
from routes.notifications import notifications_bp
from routes.content import content_bp
from routes.auth import auth_bp
from routes.roles import roles_bp
from routes.admins import admins_bp

# Register authentication and admin blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(roles_bp, url_prefix='/api/roles')
app.register_blueprint(admins_bp, url_prefix='/api/admins')

# Register existing blueprints
app.register_blueprint(subscribers_bp, url_prefix='/api/subscribers')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(leagues_bp, url_prefix='/api/leagues')
app.register_blueprint(teams_bp, url_prefix='/api/teams')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(players_bp, url_prefix='/api/players')
app.register_blueprint(reels_bp, url_prefix='/api/reels')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(content_bp, url_prefix='/api/content')

# Import sidebar manager
from utils.sidebar_manager import get_sidebar_items, get_active_sidebar_item

# Make sidebar menu available to all templates
@app.context_processor
def inject_sidebar():
    return {
        'admin_sidebar': get_sidebar_items(current_user if current_user.is_authenticated else None),
        'active_page': get_active_sidebar_item()
    }

# Add routes for documentation and login
from flask import render_template, redirect, url_for, request
from utils.auth import auth_required

@app.route('/')
@auth_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@auth_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/docs')
@auth_required
def api_docs():
    return render_template('swagger.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

# Routes for other sidebar items
@app.route('/leagues')
@auth_required
def leagues_page():
    return render_template('dashboard.html')

@app.route('/users')
@auth_required
def users_page():
    return render_template('dashboard.html')

@app.route('/subscribers')
@auth_required
def subscribers_page():
    return render_template('dashboard.html')

@app.route('/reels')
@auth_required
def reels_page():
    return render_template('dashboard.html')

@app.route('/notifications')
@auth_required
def notifications_page():
    return render_template('dashboard.html')

@app.route('/content')
@auth_required
def content_page():
    return render_template('dashboard.html')

@app.route('/roles')
@auth_required
def roles_page():
    return render_template('dashboard.html')

@app.route('/admins')
@auth_required
def admins_page():
    return render_template('dashboard.html')

# Database initialization moved to main.py
logger.info("Gambit Admin API configured")