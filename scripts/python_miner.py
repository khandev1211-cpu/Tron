import os
import hashlib
import ecdsa
import base58
import time
import multiprocessing
import redis
import json
from dotenv import load_dotenv

load_dotenv()

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, protocol=2)

def generate_tron_address():
    priv_key = os.urandom(32)
    sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pub_key = vk.to_string()

    # Simple hash (substitute for keccak in pure python)
    keccak = hashlib.sha3_256()
    keccak.update(pub_key)
    pub_key_hash = keccak.digest()

    address_bytes = b'\x41' + pub_key_hash[-20:]
    address = base58.b58encode_check(address_bytes).decode()
    return priv_key.hex(), address

def worker(prefix, suffix, pattern, result_queue, stop_event):
    while not stop_event.is_set():
        priv, addr = generate_tron_address()
        if addr.startswith(prefix) and addr.endswith(suffix):
            result_queue.put((priv, addr))
            stop_event.set()
            break

def start_attack(pattern):
    parts = pattern.split('*')
    prefix, suffix = parts[0], parts[1]

    result_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    processes = []

    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker, args=(prefix, suffix, pattern, result_queue, stop_event))
        p.start()
        processes.append(p)

    # Wait for match
    priv, addr = result_queue.get()

    for p in processes: p.terminate()

    # --- REPORT TO REDIS ---
    result_data = {
        "address": addr,
        "private_key": priv,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    r.set(f"mine_result:{pattern}", json.dumps(result_data))
    r.set(f"mine_status:{pattern}", "completed")

    # Also save to local file as backup
    with open(f"result_{pattern.replace('*','_')}.txt", "w") as f:
        f.write(json.dumps(result_data, indent=4))

if __name__ == "__main__":
    from datetime import datetime
    import sys
    if len(sys.argv) > 1:
        start_attack(sys.argv[1])
