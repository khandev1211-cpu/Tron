import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("TRON_GRID_API_KEY")
url = "https://api.trongrid.io/v1/accounts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
headers = {"TRON-PRO-API-KEY": key}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Key is valid for TronGrid.")
    else:
        print(f"Failed. Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
