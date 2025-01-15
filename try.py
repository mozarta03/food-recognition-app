import time
import random
import urllib.parse
import hmac
import hashlib
import base64
import requests

def generate_oauth_signature(http_method, base_url, params, consumer_secret):
    # Create the parameter string
    params_encoded = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}" 
        for k, v in sorted(params.items())
    )
    # Create the signature base string
    signature_base_string = f"{http_method.upper()}&{urllib.parse.quote(base_url, safe='')}&{urllib.parse.quote(params_encoded, safe='')}"
    
    # Create the signing key
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&"
    
    # Generate the HMAC-SHA1 signature
    hashed = hmac.new(signing_key.encode(), signature_base_string.encode(), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode()
    
    return signature

# OAuth parameters
consumer_key = "77eb89f1c992409d9139a388362dc692"
consumer_secret = "YOUR_CONSUMER_SECRET"  # Replace with your secret
oauth_timestamp = str(int(time.time()))
oauth_nonce = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10))
oauth_signature_method = "HMAC-SHA1"
oauth_version = "1.0"

# Request parameters
base_url = "https://platform.fatsecret.com/rest/foods/search/v2"
params = {
    "search_expression": "macarons",
    "format": "json",
    "page_number": "0",
    "max_results": "5",
    "oauth_consumer_key": consumer_key,
    "oauth_nonce": oauth_nonce,
    "oauth_signature_method": oauth_signature_method,
    "oauth_timestamp": oauth_timestamp,
    "oauth_version": oauth_version,
}

# Generate the OAuth signature
oauth_signature = generate_oauth_signature("GET", base_url, params, consumer_secret)
params["oauth_signature"] = oauth_signature

# Construct the Authorization header
auth_header = (
    f'OAuth oauth_consumer_key="{consumer_key}", '
    f'oauth_nonce="{oauth_nonce}", '
    f'oauth_signature_method="{oauth_signature_method}", '
    f'oauth_timestamp="{oauth_timestamp}", '
    f'oauth_version="{oauth_version}", '
    f'oauth_signature="{urllib.parse.quote(oauth_signature, safe="")}"'
)

# Make the request
headers = {
    "Authorization": auth_header,
}
response = requests.get(base_url, headers=headers, params=params)

print(response.text)
