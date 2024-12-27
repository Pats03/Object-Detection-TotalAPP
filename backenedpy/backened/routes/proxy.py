# routes/proxy.py
from flask import Blueprint, request, send_file, jsonify
import requests
from io import BytesIO

# Define the blueprint for the proxy
proxy_bp = Blueprint('proxy', __name__)

# Proxy route to fetch image from external URL
@proxy_bp.route('/proxy', methods=['GET'])
def proxy():
    # Get the external URL from the query parameters
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Make a request to the external URL to fetch the image
        response = requests.get(url)

        # If the response status is not 200, return an error
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch image"}), 500

        # Ensure the content is an image
        content_type = response.headers['Content-Type']
        if not content_type.startswith('image/'):
            return jsonify({"error": "The URL did not return an image"}), 400

        # Send the image back to the frontend
        img = BytesIO(response.content)
        return send_file(img, mimetype=content_type)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
