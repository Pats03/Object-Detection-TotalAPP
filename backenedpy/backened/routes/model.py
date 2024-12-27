from flask import Blueprint, request, jsonify
import requests
import numpy as np
from PIL import Image
import torch
import os

# Blueprint for model routes
model_bp = Blueprint('model', __name__)

# Function to process and flatten an image
def image_to_array(image_path):
    image = Image.open(image_path)
    image = image.convert('L')  # Convert to grayscale
    image = image.resize((120, 120))  # Resize image
    image_array = np.array(image) / 255.0  # Normalize pixel values
    return np.expand_dims(image_array, axis=0)  # Add channel dimension

# Load Pretrained Weights
weights_file = os.path.join(os.path.dirname(__file__), "weights_training.pt")

# Ensure weights file exists
if not os.path.exists(weights_file):
    raise FileNotFoundError(f"Weight file not found: {weights_file}")

# Convolution Layer
class ConvLayer:
    def __init__(self, num_filters, kernel_size, stride=1, padding=0):
        self.num_filters = num_filters
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.filters = np.random.randn(num_filters, kernel_size, kernel_size) * 0.1

    def _apply_padding(self, input_image):
        if self.padding == 0:
            return input_image
        else:
            return np.pad(input_image, ((0, 0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')

    def forward(self, input_image):
        self.input_image = input_image
        input_image = self._apply_padding(input_image)
        num_channels, h, w = input_image.shape
        output_dim = ((h - self.kernel_size) // self.stride) + 1
        output = np.zeros((self.num_filters, output_dim, output_dim))

        for f in range(self.num_filters):
            filter = self.filters[f]
            for i in range(0, output_dim):
                for j in range(0, output_dim):
                    region = input_image[:, i * self.stride:i * self.stride + self.kernel_size, j * self.stride:j * self.stride + self.kernel_size]
                    output[f, i, j] = np.sum(region * filter)
        return output

# Max Pooling Layer
class MaxPoolingLayer:
    def __init__(self, pool_size=2, stride=2):
        self.pool_size = pool_size
        self.stride = stride

    def forward(self, input_image):
        num_filters, h, w = input_image.shape
        output_dim = ((h - self.pool_size) // self.stride) + 1
        output = np.zeros((num_filters, output_dim, output_dim))

        for f in range(num_filters):
            for i in range(0, h - self.pool_size + 1, self.stride):
                for j in range(0, w - self.pool_size + 1, self.stride):
                    region = input_image[f, i:i + self.pool_size, j:j + self.pool_size]
                    output[f, i // self.stride, j // self.stride] = np.max(region)

        return output

# ReLU Activation
class Activation_ReLU:
    def forward(self, inputs):
        self.output = np.maximum(0, inputs)

# Flatten Layer
class FlattenLayer:
    def forward(self, inputs):
        self.output = inputs.flatten().reshape(1, -1)

# Dense Layer with Xavier Initialization
class Layer_dense:
    def __init__(self, inputs, neurons):
        self.weights = np.random.randn(inputs, neurons) * np.sqrt(2. / (inputs + neurons)).astype(np.float32)
        self.biases = np.zeros((1, neurons), dtype=np.float32)

    def forward(self, inputs):
        self.input = inputs
        self.output = np.dot(inputs, self.weights) + self.biases

# Output Layer
class OutputLayer:
    def __init__(self, inputs):
        self.weights = np.random.randn(inputs, 1) * 0.01
        self.biases = np.zeros((1, 1), dtype=np.float32)

    def forward(self, inputs):
        self.output = np.dot(inputs, self.weights) + self.biases

# Load Pretrained Weights
def load_pretrained_weights():
    weights = torch.load(weights_file)
    conv1.filters = weights["conv1"]
    conv2.filters = weights["conv2"]
    dense1.weights = weights["dense1_weights"]
    dense1.biases = weights["dense1_biases"]
    output_layer.weights = weights["output_weights"]
    output_layer.biases = weights["output_biases"]
    print(f"Weights loaded from {weights_file}")

# Model Layers
conv1 = ConvLayer(num_filters=32, kernel_size=3, stride=1, padding=1)
pool1 = MaxPoolingLayer(pool_size=2, stride=2)
activation1 = Activation_ReLU()
conv2 = ConvLayer(num_filters=64, kernel_size=3, stride=1, padding=1)
pool2 = MaxPoolingLayer(pool_size=2, stride=2)
activation2 = Activation_ReLU()
flatten = FlattenLayer()
dense1 = Layer_dense(64 * 30 * 30, 128)
output_layer = OutputLayer(128)

# Load pretrained weights
load_pretrained_weights()

# Function to predict the count
def predict_count(image_path):
    # Preprocess the image
    image_array = image_to_array(image_path)
    if image_array is None:
        print(f"Failed to process image {image_path}")
        return None

    # Forward pass through the network
    conv_output1 = conv1.forward(image_array)
    activation1.forward(conv_output1)
    pool_output1 = pool1.forward(activation1.output)
    conv_output2 = conv2.forward(pool_output1)
    activation2.forward(conv_output2)
    pool_output2 = pool2.forward(activation2.output)
    flatten.forward(pool_output2)
    dense1.forward(flatten.output)
    output_layer.forward(dense1.output)

    # Predicted count
    predicted_count = output_layer.output[0][0] * 100  # Scale back to original range
    return predicted_count


@model_bp.route('/predict', methods=['POST'])
def predict():
    # Extract JSON payload
    data = request.json

    if not data or 'image_url' not in data:
        return jsonify({'error': 'No image URL provided'}), 400

    image_url = data['image_url']
    
    try:
        # Download the image from the URL and process it
        image_path = download_image(image_url)  # You need to implement a function to download the image
        
        # Predict the count
        predicted_count = predict_count(image_path)

        if predicted_count is not None:
            return jsonify({'predicted_count': predicted_count}), 200
        else:
            return jsonify({'error': 'Prediction failed'}), 500

    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500


# Helper function to download the image from a URL
def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        # Save the image to a local path
        image_path = 'temp_image.jpg'  # You can modify the path as necessary
        with open(image_path, 'wb') as f:
            f.write(response.content)
        return image_path
    else:
        raise Exception('Failed to download image')
