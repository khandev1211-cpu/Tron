import os
import hashlib
import ecdsa
import base58
import time
import multiprocessing

def generate_addr():
    priv = os.urandom(32)
    sk = ecdsa.SigningKey.from_string(priv, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pub = vk.to_string()
    # Tron Hash
    keccak = hashlib.sha3_256()
    keccak.update(pub)
    pub_hash = keccak.digest()
    addr_bytes = b'\x41' + pub_hash[-20:]
    return base58.b58encode_check(addr_bytes).decode()

def run_test(duration=10):
    print(f"--- SENTINEL SPEED TEST (CPU Multi-Core) ---")
    print(f"Cores Detected: {multiprocessing.cpu_count()}")
    print(f"Running for {duration} seconds to measure performance...\n")

    start = time.time()
    count = 0
    # Simple loop for speed measurement (Single core measurement first)
    while time.time() - start < duration:
        generate_addr()
        count += 1

    elapsed = time.time() - start
    total_speed = (count * multiprocessing.cpu_count()) / elapsed # Estimated multi-core speed

    print(f"[*] Raw Speed: ~{int(total_speed)} addresses/second")

    # 3+3 Prediction
    prob_3_3 = 58**6 # Approximate for 6 chars
    time_3_3 = prob_3_3 / total_speed

    # 5+5 Prediction
    prob_5_5 = 58**10
    time_5_5 = prob_5_5 / total_speed

    print(f"\n--- TIME PREDICTIONS (Estimated) ---")
    print(f"3+3 Match (e.g. TABC...XYZ): ~{round(time_3_3 / 60, 2)} minutes")
    print(f"5+5 Match (e.g. TABCDE...VWXYZ): ~{round(time_5_5 / 86400, 2)} days")

    print("\n[!] NOTE: GPU mining is 100x to 1000x faster than this CPU test.")

if __name__ == "__main__":
    run_test()
