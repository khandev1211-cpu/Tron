import os
import time
import json
import redis
import subprocess
import platform
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Config
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
GPU_PATH = os.getenv("GPU_MINER_PATH")

def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        protocol=2,
        socket_timeout=None,
        socket_keepalive=True
    )

r = get_redis_client()

def get_gpu_count():
    try:
        output = subprocess.check_output(["nvidia-smi", "-L"], text=True)
        return len(re.findall(r"GPU \d+:", output))
    except:
        return 1

def run_gpu_miner(pattern):
    current_os = platform.system()
    prefix_len = int(os.getenv("GPU_PREFIX_MATCH_LEN", 3))
    suffix_len = int(os.getenv("GPU_SUFFIX_MATCH_LEN", 3))
    timeout = int(os.getenv("GPU_MINING_TIMEOUT", 120))

    if '*' in pattern:
        parts = pattern.split('*')
    elif '...' in pattern:
        parts = pattern.split('...')
    else:
        parts = [pattern[:5], pattern[-5:]]

    p_raw = parts[0][1:] if parts[0].startswith('T') else parts[0]
    s_raw = parts[1]

    prefix = p_raw[:prefix_len]
    suffix = s_raw[-suffix_len:]

    # Check if local GPU miner executable exists
    if not GPU_PATH or not os.path.exists(GPU_PATH):
        # Local GPU executable not installed on Brain VPS -- delegated to external Remote GPU Node (TronVanity)
        print(f"[*] Task '{pattern}' delegated to external Remote GPU Node (TronVanity)...")
        start_t = time.time()
        while time.time() - start_t < timeout:
            res_raw = r.get(f"mine_result:{pattern}")
            if res_raw:
                try:
                    res = json.loads(res_raw)
                    return res.get("address"), res.get("private_key")
                except: pass
            time.sleep(1)
        return None, None

    result_id = int(time.time())
    result_file = f"match_{result_id}.txt"

    base58_pad = "123456789ABCDEFGHJKLMNPQRSTUV"
    pad_needed = 34 - 1 - len(prefix) - len(suffix)
    dummy_fill = base58_pad[:pad_needed]
    target_address = f'T{prefix}{dummy_fill}{suffix}'

    cmd = [
        GPU_PATH,
        "--matching", target_address,
        "--prefix-count", str(len(prefix)),
        "--suffix-count", str(len(suffix)),
        "--quit-count", "1",
        "--skip", "1" if current_os == "Windows" else "0",
        "--output", result_file
    ]

    try:
        if current_os == "Windows":
            batch_content = f'@echo off\n"{GPU_PATH}" --matching {target_address} --prefix-count {len(prefix)} --suffix-count {len(suffix)} --quit-count 1 --skip 1 --output "{result_file}"\nexit'
            batch_path = os.path.join(os.getcwd(), f"run_gpu_{result_id}.bat")
            with open(batch_path, "w") as f: f.write(batch_content)

            proc = subprocess.Popen(["cmd", "/c", batch_path], creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"[*] Local GPU Attack: T{prefix}...{suffix} (Watching result file...)")

            for _ in range(timeout * 2):
                if os.path.exists(result_file) and os.path.getsize(result_file) > 10:
                    with open(result_file, "r") as f:
                        content = f.read().strip()
                        if "," in content:
                            priv, addr = content.split(",", 1)
                            priv = priv.strip()
                            addr = addr.strip()
                            if addr and priv:
                                try: os.remove(batch_path); os.remove(result_file)
                                except: pass
                                return addr, priv
                time.sleep(0.5)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"[*] Multi-GPU Engine Attack: T{prefix}...{suffix}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            start_t = time.time()

            while time.time() - start_t < timeout:
                if os.path.exists(result_file) and os.path.getsize(result_file) > 10:
                    with open(result_file, "r") as f:
                        content = f.read().strip()
                        if "," in content:
                            priv, addr = content.split(",", 1)
                            priv, addr = priv.strip(), addr.strip()
                            process.terminate()
                            try: os.remove(result_file)
                            except: pass
                            return addr, priv
                time.sleep(0.5)
        return None, None
    except Exception as e:
        print(f"Engine Error: {e}")
        return None, None

def process_queue():
    gpu_count = get_gpu_count()
    print(f"--- SENTINEL TURBO ENGINE ACTIVE ---")
    print(f"[*] Detected GPUs/Nodes: {gpu_count}")

    while True:
        try:
            task_data = r.brpop("gpu_queue", timeout=30)
            if task_data is None: continue

            task = json.loads(task_data[1])
            pattern = task['pattern']

            # Check if remote GPU worker (TronVanity) is processing or has processed it
            mine_status = r.get(f"mine_status:{pattern}")
            if mine_status == "mining" or mine_status == "completed":
                # Already being handled by external GPU worker (TronVanity)
                continue

            r.set(f"mine_status:{pattern}", "mining")
            r.set(f"mine_mode:{pattern}", f"{gpu_count}x GPU Distributed Turbo")

            print(f"\n[+] TASK RECEIVED: {pattern} on {gpu_count} Nodes")
            addr, priv = run_gpu_miner(pattern)

            if addr and priv:
                result = {"address": addr, "private_key": priv, "time": datetime.now().strftime("%H:%M:%S")}
                r.set(f"mine_result:{pattern}", json.dumps(result))
                r.set(f"mine_status:{pattern}", "completed")
                print(f"[✅] SUCCESS: Match synced across nodes.")
            else:
                # If local VPS GPU miner wasn't available, check if Remote GPU Node completed it while waiting
                res_raw = r.get(f"mine_result:{pattern}")
                if res_raw:
                    print(f"[✅] SUCCESS: Remote GPU Node completed match.")
                else:
                    r.set(f"mine_status:{pattern}", "error")
                    print(f"[❌] TIMEOUT.")
        except Exception as e:
            print(f"Queue error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    process_queue()
