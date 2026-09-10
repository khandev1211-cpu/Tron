import requests
import json
from datetime import datetime

def check_history(address):
    print(f"--- Checking Real-Time History for Target: {address} ---")
    url = f"https://api.trongrid.io/v1/accounts/{address}/events"
    params = {
        "event_name": "Transfer",
        "limit": 5,
        "only_confirmed": True
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        events = data.get('data', [])

        if not events:
            print("No recent USDT transfers found for this address in the last few hours.")
            return

        for ev in events:
            res = ev.get('result', {})
            val = int(res.get('value', 0)) / 10**6
            ts = ev.get('block_timestamp')
            dt = datetime.fromtimestamp(ts/1000)
            print(f"[{dt}] Value: {val} USDT | From: {res.get('from')} | To: {res.get('to')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # The address you identified
    target = "TVPQLkVXvN7MduHWhD4Q7rGVyRdDu5R8F6"
    check_history(target)
