import os
import time
import redis
import requests
from decimal import Decimal
from dotenv import load_dotenv

# Load configuration
load_dotenv()

TRON_GRID_API_KEY = os.getenv("TRON_GRID_API_KEY")
TRONSCAN_API_KEY = os.getenv("TRONSCAN_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
USDT_CONTRACT = os.getenv("USDT_CONTRACT", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
MIN_BALANCE = Decimal(os.getenv("MIN_USDT_BALANCE", "7499"))
REDIS_TTL = int(os.getenv("REDIS_TTL", 86400))

# Exclusion characters (Base58Check ambiguous chars)
EXCLUSION_CHARS = {'0', 'O', 'I', 'l'}

def is_valid_pattern(address):
    """Checks if the address pattern contains ambiguous characters."""
    if not address or len(address) < 10:
        return False

    # Pattern is first 4 after 'T' and last 5
    first_4 = address[1:5]
    last_5 = address[-5:]

    combined = first_4 + last_5
    for char in combined:
        if char in EXCLUSION_CHARS:
            return False
    return True

def get_pattern(address):
    """Extracts the 4x5 pattern."""
    return f"{address[1:5]}*{address[-5:]}"

def scan_usdt_holders():
    """
    Scans for top USDT holders.
    Note: TronGrid doesn't provide a direct 'list all accounts by token balance' API.
    In a real scenario, this would use TronScan's holders API or a local DB.
    For this implementation, we will use TronScan's token holders endpoint.
    """
    url = f"https://apilist.tronscan.org/api/token_trc20/holders?contract_address={USDT_CONTRACT}&start=0&limit=100&sort=balance"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Origin": "https://api.trongrid.io/get"
    }
    if TRONSCAN_API_KEY:
        headers["apiKey"] = TRONSCAN_API_KEY
    elif TRON_GRID_API_KEY:
        headers["TRON-PRO-API-KEY"] = TRON_GRID_API_KEY

    try:
        response = requests.get(url, headers=headers, timeout=15)

        response.raise_for_status()
        data = response.json()

        holders = data.get("trc20_tokens", [])
        return holders
    except Exception as e:
        print(f"Error fetching holders: {e}")
        return []

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    print("Connected to Redis. Starting harvester...")

    holders = scan_usdt_holders()
    count = 0

    # Use pipeline for efficiency
    pipe = r.pipeline()

    for holder in holders:
        address = holder.get("address")
        if not address:
            continue

        # TronScan balance is usually in units (6 decimals for USDT)
        balance = Decimal(holder.get("balance", "0")) / Decimal(10**6)

        if balance >= MIN_BALANCE:
            if is_valid_pattern(address):
                pattern = get_pattern(address)
                # Store pattern as key, address as value (or just track the pattern)
                # The requirement says "stores a partial address pattern in Redis"
                # and "cross-references the sender address against the active Redis database".
                # To lookup in < 1ms, we store the pattern as a key for fast existence check.
                redis_key = f"target:{pattern}"
                pipe.setex(redis_key, REDIS_TTL, address)
                count += 1
            else:
                print(f"Skipping {address} due to ambiguous characters in pattern.")
        else:
            # Since holders are sorted by balance, we can stop early if we want,
            # but usually the API returns a page, so we just filter.
            pass

    pipe.execute()
    print(f"Successfully harvested {count} wallet patterns into Redis.")

if __name__ == "__main__":
    main()
