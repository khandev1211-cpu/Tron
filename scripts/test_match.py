import redis
import json
import os
import sys
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add scripts to path
sys.path.append(os.path.join(os.getcwd(), "scripts"))
from monitor_agent import MonitorAgent

def test_manual_match():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, protocol=2)

    # 1. Get a real target from Redis
    keys = r.keys("target:*")
    if not keys:
        print("❌ No targets found in Redis. Run harvester first.")
        return

    target_key = keys[0]
    target_data = json.loads(r.get(target_key))
    address = target_data['address']
    balance = target_data['balance']
    pattern = target_key.replace("target:", "")

    print(f"Testing with Target: {address} (Pattern: {pattern}, Balance: {balance})")

    # 2. Simulate an event
    event = {
        'result': {
            'from': address,
            'to': 'TReceiverAddressTest123456789',
            'value': '250000000' # 250 USDT
        },
        'block_timestamp': int(datetime.now().timestamp() * 1000)
    }

    # 3. Use MonitorAgent logic to process
    agent = MonitorAgent()
    # Mocking redis to use our local connection
    agent.r = r

    print("Running process_event...")
    agent.process_event(event)

    # 4. Check if match_history has new entries
    history = r.lrange("match_history", 0, 0)
    if history:
        latest = json.loads(history[0])
        if latest['address'] == address:
            print(f"✅ SUCCESS: Match detected and stored in Redis!")
            print(f"Data: {latest}")
        else:
            print("❌ Match found but address mismatch in history.")
    else:
        print("❌ FAILED: No match stored in match_history.")

if __name__ == "__main__":
    test_manual_match()
