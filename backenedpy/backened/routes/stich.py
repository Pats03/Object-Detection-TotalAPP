from flask import Blueprint, request, send_file, jsonify
import requests
from io import BytesIO
from PIL import Image
import os
import io

stich_bp = Blueprint('stich', __name__)

def stitch_images(img1, img2):
    # Resize images to have the same height while maintaining aspect ratio
    height = max(img1.height, img2.height)
    width1 = int(img1.width * (height / img1.height))
    width2 = int(img2.width * (height / img2.height))

    img1_resized = img1.resize((width1, height))
    img2_resized = img2.resize((width2, height))

    new_image = Image.new('RGB', (width1 + width2, height))
    new_image.paste(img1_resized, (0, 0))
    new_image.paste(img2_resized, (width1, 0))

    return new_image


@stich_bp.route('/stitch', methods=['POST', 'OPTIONS'])
def handle_stitch():
    # For preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        return '', 200

    # Check if both image files are provided
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({"error": "Both images must be provided"}), 400
    
    image1 = Image.open(request.files['image1']).convert("RGB")
    image2 = Image.open(request.files['image2']).convert("RGB")

    stitched_img = stitch_images(image1, image2)
    img_io = io.BytesIO()
    stitched_img.save(img_io, format='JPEG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/jpeg')

  