import time
import random
import hashlib
import hmac
import base64
import urllib.parse
import requests

# Function to generate OAuth signature
def generate_oauth_signature(http_method, url, params, consumer_secret, token_secret=None):
    # Step 1: Create the signature base string
    # Sort parameters by key
    sorted_params = sorted(params.items())
    normalized_params = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)

    # Create base string
    base_string = '&'.join([http_method.upper(), urllib.parse.quote(url, safe=''), urllib.parse.quote(normalized_params, safe='')])

    # Step 2: Generate the signing key (consumer secret and token secret)
    signing_key = f"{urllib.parse.quote(consumer_secret)}&{urllib.parse.quote(token_secret or '')}"

    # Step 3: Calculate HMAC-SHA1 signature
    hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode('utf-8')

    return signature

# Function to get nutritional information from FatSecret API
def get_nutrition_info(food_name, consumer_key, consumer_secret):
    # Prepare API URL and parameters
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

    # Step 1: Generate the OAuth signature
    oauth_signature = generate_oauth_signature('GET', url, params, consumer_secret)

    # Add the oauth_signature to the parameters
    params['oauth_signature'] = oauth_signature

    # Step 2: Send the request
    headers = {
        'Authorization': f'OAuth oauth_consumer_key="{consumer_key}",'
                         f'oauth_signature_method="HMAC-SHA1",'
                         f'oauth_timestamp="{params["oauth_timestamp"]}",'
                         f'oauth_nonce="{params["oauth_nonce"]}",'
                         f'oauth_version="1.0",'
                         f'oauth_signature="{oauth_signature}"'
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # Return the nutritional information
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}

# Example usage
consumer_key = "77eb89f1c992409d9139a388362dc692"  # Your consumer key
consumer_secret = "61aee66e9dd24359a97e826bdde7d9d8"  # Your consumer secret
food_name = "fried chicken"

# Get the nutrition info
nutrition_info = get_nutrition_info(food_name, consumer_key, consumer_secret)
print(nutrition_info)
