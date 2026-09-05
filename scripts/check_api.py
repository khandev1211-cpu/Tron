import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("TRON_GRID_API_KEY")

print(f"Testing Events without Key...")
url = "https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=Transfer&limit=1"
headers = {}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
