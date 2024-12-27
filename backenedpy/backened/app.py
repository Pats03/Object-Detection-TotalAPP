from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from routes.auth import init_auth_routes
from routes.model import model_bp
from routes.proxy import proxy_bp  # Import the proxy blueprint

# Initialize Flask app
app = Flask(__name__)

# App configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/AttendanceData"

# Initialize MongoDB
mongo = PyMongo(app)

# Enable CORS
CORS(app)

# Register Blueprints
auth_bp = init_auth_routes(mongo)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(model_bp, url_prefix='/model')
app.register_blueprint(proxy_bp, url_prefix='/proxy')  # Register the proxy blueprint

# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5173)
