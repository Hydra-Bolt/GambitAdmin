import os
import logging

from flask import Flask
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Import and register routes
from routes.subscribers import subscribers_bp
from routes.users import users_bp
from routes.leagues import leagues_bp
from routes.teams import teams_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(subscribers_bp, url_prefix='/api/subscribers')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(leagues_bp, url_prefix='/api/leagues')
app.register_blueprint(teams_bp, url_prefix='/api/teams')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# Add Swagger documentation route
from flask import render_template

@app.route('/api/docs')
def api_docs():
    return render_template('swagger.html')

# Initialize mock data when app starts
from utils.mock_data import initialize_mock_data
initialize_mock_data()

logger.info("Gambit Admin API initialized")
