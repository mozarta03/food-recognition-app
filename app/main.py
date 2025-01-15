from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import torch
from app.model import predict_image  # Replace with your model's import
import json
from starlette.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import time
import random
import hashlib
import hmac
import base64
import urllib.parse
import requests

# Load the configuration file
with open('app/config.json') as config_file:
    config = json.load(config_file)
    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Mount static files directory at "/static" path
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_html():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; modify for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to generate OAuth signature for FatSecret API
def generate_oauth_signature(http_method, url, params, consumer_secret, token_secret=None):
    sorted_params = sorted(params.items())
    normalized_params = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
    base_string = '&'.join([http_method.upper(), urllib.parse.quote(url, safe=''), urllib.parse.quote(normalized_params, safe='')])
    signing_key = f"{urllib.parse.quote(consumer_secret)}&{urllib.parse.quote(token_secret or '')}"
    hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode('utf-8')
    return signature

# Function to get nutritional information from FatSecret API
def get_nutrition_info(food_name, consumer_key, consumer_secret):
    url = "https://platform.fatsecret.com/rest/foods/search/v3"
    params = {
        'search_expression': food_name,
        'format': 'json',
        'include_sub_categories': 'true',
        'flag_default_serving': 'true',
        'max_results': '10',
        'language': 'en',
        'region': 'US',
        'oauth_consumer_key': consumer_key,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_nonce': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32)),
        'oauth_version': '1.0'
    }

    oauth_signature = generate_oauth_signature('GET', url, params, consumer_secret)
    params['oauth_signature'] = oauth_signature

    headers = {
        'Authorization': f'OAuth oauth_consumer_key="{consumer_key}",'
                         f'oauth_signature_method="HMAC-SHA1",'
                         f'oauth_timestamp="{params["oauth_timestamp"]}",'
                         f'oauth_nonce="{params["oauth_nonce"]}",'
                         f'oauth_version="1.0",'
                         f'oauth_signature="{oauth_signature}"'
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Read the image and make predictions
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        prediction = predict_image(image)  # Call your model's prediction function

        # Debug: Print the predicted label
        print(f"Predicted label: {prediction}")

        # Get nutritional information for the predicted label (food name)
        nutrition_info = get_nutrition_info(prediction, consumer_key, consumer_secret)

        # Debug: Print the nutrition info response
        print(f"Nutrition info: {nutrition_info}")

        if 'error' in nutrition_info:
            raise HTTPException(status_code=500, detail=nutrition_info['error'])

        # Return the prediction and nutritional information in the response
        return {
            "filename": file.filename,
            "prediction": prediction,
            "nutrition_info": nutrition_info,
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error to the terminal
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# To run the server with uvicorn:
# uvicorn app.main:app --reload