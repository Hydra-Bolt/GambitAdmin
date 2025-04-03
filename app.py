import os
import logging

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
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

# Initialize the database with the app
db.init_app(app)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

app.register_blueprint(subscribers_bp, url_prefix='/api/subscribers')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(leagues_bp, url_prefix='/api/leagues')
app.register_blueprint(teams_bp, url_prefix='/api/teams')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(players_bp, url_prefix='/api/players')
app.register_blueprint(reels_bp, url_prefix='/api/reels')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(content_bp, url_prefix='/api/content')

# Add routes for documentation
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    return render_template('swagger.html')

# Database initialization moved to main.py
logger.info("Gambit Admin API configured")
