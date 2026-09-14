import os
import time
import json
import redis
import subprocess
import platform
import sys
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
        retry_on_timeout=True
    )

r = get_redis_client()

def get_gpu_info():
    try:
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True)
        return output.strip()
    except:
        return "Generic CPU/No GPU"

def run_gpu_miner(pattern):
    # Dynamic settings from .env
    prefix_len = int(os.getenv("GPU_PREFIX_MATCH_LEN", 2))
    suffix_len = int(os.getenv("GPU_SUFFIX_MATCH_LEN", 2))
    timeout_sec = int(os.getenv("GPU_MINING_TIMEOUT", 120))

    parts = pattern.split('*')
    p_raw = parts[0][1:] if parts[0].startswith('T') else parts[0]
    s_raw = parts[1]

    prefix = p_raw[:prefix_len]
    suffix = s_raw[-suffix_len:]

    result_id = int(time.time())
    result_file = os.path.join(os.getcwd(), f"match_{result_id}.txt")

    # ProVanity Command
    batch_content = f"""@echo off
"{GPU_PATH}" generate-tron --pattern prefix:{prefix} --pattern suffix:{suffix} --devices 0 > "{result_file}"
exit
"""
    batch_path = os.path.join(os.getcwd(), f"run_gpu_{result_id}.bat")
    with open(batch_path, "w") as f:
        f.write(batch_content)

    try:
        proc = subprocess.Popen(["cmd", "/c", batch_path], creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"[*] Mining {prefix_len}+{suffix_len} Match (T{prefix}...{suffix}) for {timeout_sec}s...")

        # Check every 0.5s
        for _ in range(timeout_sec * 2):
            if os.path.exists(result_file) and os.path.getsize(result_file) > 10:
                try:
                    with open(result_file, "r") as f:
                        content = f.read()
                        if "address:" in content.lower() and "private key:" in content.lower():
                            addr, priv = None, None
                            for line in content.split('\n'):
                                if "address:" in line.lower(): addr = line.split(":")[1].strip()
                                if "private key:" in line.lower(): priv = line.split(":")[1].strip()

                            if addr and priv:
                                print(f"[+] Match found in file!")
                                return addr, priv
                except:
                    pass # File might be busy
            time.sleep(0.5)

        print("[!] Timeout reached. Killing GPU process...")
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return None, None
    except Exception as e:
        print(f"Engine Error: {e}")
        return None, None

def process_queue():
    gpu_name = get_gpu_info()
    print(f"--- SENTINEL GPU FIFO ENGINE ---")
    print(f"[*] HARDWARE: {gpu_name}")

    while True:
        try:
            # Refresh settings each loop
            load_dotenv(override=True)
            p_len = os.getenv("GPU_PREFIX_MATCH_LEN")
            s_len = os.getenv("GPU_SUFFIX_MATCH_LEN")

            task_data = r.brpop("gpu_queue", timeout=30)
            if task_data is None: continue

            task = json.loads(task_data[1])
            pattern = task['pattern']
            print(f"\n[+] TASK: {pattern} | CONFIG: {p_len}+{s_len}")

            r.set(f"mine_status:{pattern}", "mining")
            r.set(f"mine_mode:{pattern}", f"{gpu_name} ({p_len}+{s_len})")

            addr, priv = run_gpu_miner(pattern)

            if addr and priv:
                result = {"address": addr, "private_key": priv, "time": datetime.now().strftime("%H:%M:%S")}
                r.set(f"mine_result:{pattern}", json.dumps(result))
                r.set(f"mine_status:{pattern}", "completed")
                print(f"[✅] SUCCESS: Results saved to Dashboard.")
            else:
                r.set(f"mine_status:{pattern}", "error")
                print(f"[❌] FAILED: Pattern not found on this hardware.")

        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    process_queue()
