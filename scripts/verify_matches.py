import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

def verify():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, protocol=2)

    # Get all target addresses from Redis
    target_keys = r.keys("target:*")
    target_addresses = set()
    for k in target_keys:
        try:
            data = json.loads(r.get(k))
            target_addresses.add(data['address'])
        except:
            continue

    # Get all matches from history
    match_history = r.lrange("match_history", 0, -1)

    print(f"--- Sentinel Verification Report ---")
    print(f"Total Unique Targets in Redis: {len(target_addresses)}")
    print(f"Total Matches in Feed: {len(match_history)}")
    print("-----------------------------------")

    valid_count = 0
    invalid_matches = []

    for m in match_history:
        try:
            match = json.loads(m)
            addr = match['address']
            if addr in target_addresses:
                valid_count += 1
                # print(f"[VALID] Match for {addr} (Value: {match['value']} USDT)")
            else:
                invalid_matches.append(addr)
        except:
            continue

    print(f"✅ Verified Matches: {valid_count}")
    if invalid_matches:
        print(f"❌ Invalid Matches (Not in 50 targets): {len(invalid_matches)}")
        for addr in invalid_matches:
            print(f"   - {addr}")
    else:
        print(f"✅ All matches in the feed belong strictly to your harvested targets.")

if __name__ == "__main__":
    verify()
