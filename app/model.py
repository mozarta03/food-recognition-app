import torch
from torchvision import transforms
from PIL import Image
from typing import List

# Load the trained ResNet-50 model
model_path = 'resnet50.pt'
model = torch.load(model_path, map_location=torch.device('cpu'))
model.eval()  # Set the model to evaluation mode

# Define preprocessing transformations
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Define class labels (Update with your Food-101 dataset classes)
LABELS = [
    'apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare', 'beet_salad', 'beignets', 'bibimbap',
           'bread_pudding', 'breakfast_burrito', 'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad', 'carrot_cake', 
           'ceviche', 'cheese_plate', 'cheesecake', 'chicken_curry', 'chicken_quesadilla', 'chicken_wings', 'chocolate_cake', 
           'chocolate_mousse', 'churros', 'clam_chowder', 'club_sandwich', 'crab_cakes', 'creme_brulee', 'croque_madame', 'cup_cakes', 
           'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict', 'escargots', 'falafel', 'filet_mignon', 'fish_and_chips', 
           'foie_gras', 'french_fries', 'french_onion_soup', 'french_toast', 'fried_calamari', 'fried_rice', 'frozen_yogurt', 
           'garlic_bread', 'gnocchi', 'greek_salad', 'grilled_cheese_sandwich', 'grilled_salmon', 'guacamole', 'gyoza', 'hamburger', 
           'hot_and_sour_soup', 'hot_dog', 'huevos_rancheros', 'hummus', 'ice_cream', 'lasagna', 'lobster_bisque', 'lobster_roll_sandwich', 
           'macaroni_and_cheese', 'macarons', 'miso_soup', 'mussels', 'nachos', 'omelette', 'onion_rings', 'oysters', 'pad_thai', 'paella', 
           'pancakes', 'panna_cotta', 'peking_duck', 'pho', 'pizza', 'pork_chop', 'poutine', 'prime_rib', 'pulled_pork_sandwich', 
           'ramen', 'ravioli', 'red_velvet_cake', 'risotto', 'samosa', 'sashimi', 'scallops', 'seaweed_salad', 'shrimp_and_grits', 
           'spaghetti_bolognese', 'spaghetti_carbonara', 'spring_rolls', 'steak', 'strawberry_shortcake', 'sushi', 'tacos', 'takoyaki', 'tiramisu', 'tuna_tartare', 'waffles'
]

import torch
from PIL import Image

# Assuming your model is loaded as 'model' and 'preprocess' is your preprocessing function.
# You might want to add a check here to ensure that model is loaded.

def predict_image(image: Image.Image) -> str:
    """
    Predict the label of the given image using the loaded ResNet-50 model.
    """
    try:
        # Log image details for debugging
        print(f"Image format: {image.format}, size: {image.size}, mode: {image.mode}")

        # Preprocess the image (ensure 'preprocess' is defined elsewhere in your code)
        image_tensor = preprocess(image).unsqueeze(0)  # Add batch dimension
        print(f"Image tensor shape: {image_tensor.shape}")

        # Ensure model is in evaluation mode
        model.eval()

        # Make the prediction
        with torch.no_grad():
            outputs = model(image_tensor)
            _, predicted_class = torch.max(outputs, 1)

        predicted_label = LABELS[predicted_class.item()]
        print(f"Predicted label: {predicted_label}")
        
        return predicted_label

    except Exception as e:
        # Log error details
        print(f"Prediction failed: {str(e)}")
        raise ValueError(f"Prediction failed: {str(e)}")

