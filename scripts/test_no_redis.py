import os
import requests
from decimal import Decimal
from dotenv import load_dotenv

# Load configuration
load_dotenv()

TRON_GRID_API_KEY = os.getenv("TRON_GRID_API_KEY")
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
MIN_BALANCE = Decimal("7499")
EXCLUSION_CHARS = {'0', 'O', 'I', 'l'}

def is_valid_pattern(address):
    first_4 = address[1:5]
    last_5 = address[-5:]
    combined = first_4 + last_5
    for char in combined:
        if char in EXCLUSION_CHARS:
            return False
    return True

def get_pattern(address):
    return f"{address[1:5]}*{address[-5:]}"

def test_harvester_logic():
    print(f"--- Testing Harvester Logic (Mock Data) ---")

    # Mock data to simulate API response
    holders = [
        {"address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "balance": "1000000000000"}, # Rich, Valid
        {"address": "T0xO1l23456789ABCDEFGHJ1234567890", "balance": "500000000000"},  # Rich, Invalid (has 0, O, I, l)
        {"address": "TM123456789ABCDEFGHJ123456789XYZ", "balance": "8000000000"},    # Rich, Valid
        {"address": "TPoorWalletAddress123456789XYZ12", "balance": "100000000"}       # Poor (< 7499)
    ]

    count = 0
    for holder in holders:
        address = holder.get("address")
        balance = Decimal(holder.get("balance", "0")) / Decimal(10**6)

        if balance >= MIN_BALANCE:
            if is_valid_pattern(address):
                pattern = get_pattern(address)
                print(f"[MATCH] Address: {address}")
                print(f"        Balance: {balance:,.2f} USDT")
                print(f"        Pattern: {pattern}")
                print(f"        Action: Would be saved to Redis\n")
                count += 1
            else:
                print(f"[SKIP]  Address: {address} (Contains ambiguous chars: 0, O, I, or l)\n")
        else:
            print(f"[LOW]   Address: {address} (Balance {balance} < {MIN_BALANCE})\n")

    print(f"--- Test Finished ---")
    print(f"Total Valid Targets Found: {count}")

if __name__ == "__main__":
    test_harvester_logic()
