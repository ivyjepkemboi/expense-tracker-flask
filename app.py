import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from db import db
from routes.auth_routes import auth_bp
from routes.expense_routes import expense_bp
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(expense_bp, url_prefix="/expenses")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT not set
    app.run(host="0.0.0.0", port=port, debug=True)
