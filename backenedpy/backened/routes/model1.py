import torch
from torchvision import transforms
from PIL import Image
import torchvision.models as models
import pandas as pd
import os
from torchvision.models import EfficientNet_V2_S_Weights
import requests
from io import BytesIO


# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define the Model Class again to load the weights
class StudentCountModel(torch.nn.Module):
    def __init__(self, num_outputs=3):
        super(StudentCountModel, self).__init__()
        # Load pre-trained EfficientNetV2-S model
        self.efficientnet = models.efficientnet_v2_s(weights=EfficientNet_V2_S_Weights.DEFAULT)
        
        # Modify the final fully connected layer to output 3 values (Total, Duplicates, Originals)
        self.efficientnet.classifier[1] = torch.nn.Linear(self.efficientnet.classifier[1].in_features, num_outputs)
    
    def forward(self, x):
        return self.efficientnet(x)

# Initialize the model
model = StudentCountModel().to(device)

# Load the trained weights
# Explicitly map the model to the appropriate device
model.load_state_dict(torch.load('backenedpy/backened/routes/efficientnet-v2.pth', map_location=device))

model.eval()  # Set the model to evaluation mode

# Define the image transformation (same as used during training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize the image to match the input size of EfficientNetV2
    transforms.ToTensor(),  # Convert image to a tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize image
])

# Load the ground truth labels from CSV
# labels_df = pd.read_csv('dataset/labels.csv')

# Function to predict counts for a new image


def predict_count(image_path):
    # Check if the input is a URL or a local file path
    print("came_here")
    if image_path.startswith('http'):
        # If it's a URL, download the image
        response = requests.get(image_path)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        # If it's a local file path, open the image directly
        image = Image.open(image_path).convert("RGB")

    # Apply the necessary transformations to the image
    image = transform(image).unsqueeze(0).to(device)  # Add batch dimension and move to GPU if available

    # Predict with the trained model
    with torch.no_grad():
        output = model(image)
    
    # Get the predicted counts
    total, duplicates, originals = output.cpu().numpy()[0]
    
    # Return the counts
    return total, duplicates, originals




# # Initialize variables for efficiency calculation
# total_error = 0
# duplicate_error = 0
# original_error = 0
# total_images = len(labels_df)

# # Loop through all images in the dataset
# for idx, row in labels_df.iterrows():
#     image_name = row['filename']
#     image_path = os.path.join('dataset/images', image_name)
    
#     # Get the ground truth from the CSV
#     ground_truth_total = row['total']
#     ground_truth_duplicates = row['duplicates']
#     ground_truth_originals = row['original']
    
#     # Predict the counts using the model
#     predicted_total, predicted_duplicates, predicted_originals = predict_count(image_path)
    
#     # Calculate error for each type (Mean Absolute Error)
#     total_error += abs(predicted_total - ground_truth_total)
#     duplicate_error += abs(predicted_duplicates - ground_truth_duplicates)
#     original_error += abs(predicted_originals - ground_truth_originals)
    
#     # Calculate and print the efficiency for each image
#     image_total_error = abs(predicted_total - ground_truth_total)
#     image_duplicate_error = abs(predicted_duplicates - ground_truth_duplicates)
#     image_original_error = abs(predicted_originals - ground_truth_originals)
    
#     print(f"Image: {image_name}")
#     print(f"  Ground Truth - Total: {ground_truth_total}, Duplicates: {ground_truth_duplicates}, Originals: {ground_truth_originals}")
#     print(f"  Prediction - Total: {predicted_total:.2f}, Duplicates: {predicted_duplicates:.2f}, Originals: {predicted_originals:.2f}")
#     print(f"  Efficiency (Error) - Total: {image_total_error:.2f}, Duplicates: {image_duplicate_error:.2f}, Originals: {image_original_error:.2f}")
#     print("-" * 50)

# # Calculate the overall prediction efficiency for each type
# avg_total_error = total_error / total_images
# avg_duplicate_error = duplicate_error / total_images
# avg_original_error = original_error / total_images

# # Calculate overall prediction efficiency (average across all types)
# overall_error = (avg_total_error + avg_duplicate_error + avg_original_error) / 3

# # Print the overall efficiency
# print("\nOverall Prediction Efficiency:")
# print(f"Prediction Efficiency for Total Students: {avg_total_error:.2f}")
# print(f"Prediction Efficiency for Duplicate Students: {avg_duplicate_error:.2f}")
# print(f"Prediction Efficiency for Original Students: {avg_original_error:.2f}")
# print(f"Overall Prediction Efficiency: {overall_error:.2f}")

# Add custom image prediction at the end
# custom_image_path = './dataset/images/img10.jpg'  # Replace with the path to your custom image
# custom_image_path = ''  # Replace with the path to your custom image
# predicted_total, predicted_duplicates, predicted_originals = predict_count(custom_image_path)

# # Print the prediction for the custom image
# print("\nCustom Image Prediction:")
# print(f"Prediction for Custom Image - Total: {predicted_total:.2f}, Duplicates: {predicted_duplicates:.2f}, Originals: {predicted_originals:.2f}")