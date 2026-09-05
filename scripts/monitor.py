import os
import time
import redis
import requests
from decimal import Decimal
from dotenv import load_dotenv

# Load configuration
load_dotenv()

TRON_GRID_API_KEY = os.getenv("TRON_GRID_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
USDT_CONTRACT = os.getenv("USDT_CONTRACT", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
MIN_TRANSFER = Decimal(os.getenv("MIN_TRANSFER_THRESHOLD", "1"))
MAX_TRANSFER = Decimal(os.getenv("MAX_TRANSFER_THRESHOLD", "501"))

# Base58 ambiguous chars (same as harvester)
EXCLUSION_CHARS = {'0', 'O', 'I', 'l'}

def get_pattern(address):
    """Extracts the 4x5 pattern (ignoring 'T' prefix)."""
    return f"{address[1:5]}*{address[-5:]}"

def is_match(r, address):
    """Checks if the address pattern exists in Redis."""
    pattern = get_pattern(address)
    redis_key = f"target:{pattern}"
    return r.exists(redis_key), pattern

def process_event(r, event):
    """Processes a single Transfer event."""
    try:
        if 'result' not in event:
            return

        # Event structure for TRC-20 Transfer: {..., 'result': {'from': '...', 'to': '...', 'value': '...'}}
        sender = event['result'].get('from')
        receiver = event['result'].get('to')
        value_str = event['result'].get('value', '0')

        if not sender or not receiver:
            return

        # USDT has 6 decimals
        value = Decimal(value_str) / Decimal(10**6)

        # Check threshold
        if MIN_TRANSFER <= value <= MAX_TRANSFER:
            matched, pattern = is_match(r, sender)
            if matched:
                print(f"!!! ALERT !!! Match Found!")
                print(f"Transaction: {value} USDT from {sender} to {receiver}")
                print(f"Pattern Matched: {pattern}")
                print(f"Event Time: {event.get('timestamp')}")
                # Module C will handle Telegram alerts here
            else:
                # Silent discard for non-tracked wallets to keep console clean
                pass
    except Exception as e:
        print(f"Error processing event: {e}")

def main():
    # Initialize Redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    print(f"Monitoring USDT ({USDT_CONTRACT}) transfers...")
    print(f"Threshold: {MIN_TRANSFER} to {MAX_TRANSFER} USDT")

    # TronGrid v1 API for events
    base_url = "https://api.trongrid.io"
    headers = {
        "User-Agent": "TronSentinel/1.0",
        "Origin": "https://api.trongrid.io/get"
    }
    if TRON_GRID_API_KEY:
        headers["TRON-PRO-API-KEY"] = TRON_GRID_API_KEY

    # Get initial timestamp (milliseconds)
    since_timestamp = int(time.time() * 1000)

    while True:
        try:
            # Using requests directly for TronGrid v1 API
            url = f"{base_url}/v1/contracts/{USDT_CONTRACT}/events"
            params = {
                "event_name": "Transfer",
                "order_by": "timestamp,asc",
                "since_timestamp": since_timestamp,
                "limit": 50
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 401:
                print("Warning: TronGrid API Key returned 401 (Unauthorized). Check your dashboard settings (IP whitelist, etc.).")
                print("Attempting to continue without API Key (Rate limits will apply)...")
                if "TRON-PRO-API-KEY" in headers:
                    del headers["TRON-PRO-API-KEY"]
                continue

            response.raise_for_status()
            events = response.json()

            if events.get('success') and events.get('data'):
                data = events['data']
                for event in data:
                    process_event(r, event)
                    since_timestamp = event['timestamp'] + 1

            time.sleep(2)

        except Exception as e:
            print(f"Listener Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
