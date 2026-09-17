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
    # Setup robust connectivity params suitable for ngrok tcp tunnels
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        protocol=2,
        socket_timeout=None,
        socket_keepalive=True,
        retry_on_timeout=True
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

    parts = pattern.split('*')
    p_raw = parts[0][1:] if parts[0].startswith('T') else parts[0]
    s_raw = parts[1]

    prefix = p_raw[:prefix_len]
    suffix = s_raw[-suffix_len:]

    result_id = int(time.time())
    result_file = os.path.join(os.getcwd(), f"match_{result_id}.txt")

    # Using 'all' devices for Multi-GPU support (Vast.ai 2x 4090 support)
    cmd = [GPU_PATH, "generate-tron", "--pattern", f"prefix:{prefix}", "--pattern", f"suffix:{suffix}", "--devices", "all"]

    try:
        if current_os == "Windows":
            batch_content = f'@echo off\n"{GPU_PATH}" generate-tron --pattern prefix:{prefix} --pattern suffix:{suffix} --devices all > "{result_file}"\nexit'
            batch_path = os.path.join(os.getcwd(), f"run_gpu_{result_id}.bat")
            with open(batch_path, "w") as f: f.write(batch_content)

            proc = subprocess.Popen(["cmd", "/c", batch_path], creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"[*] Local GPU Attack: T{prefix}...{suffix} (Watching file...)")

            for _ in range(timeout * 2):
                if os.path.exists(result_file) and os.path.getsize(result_file) > 10:
                    with open(result_file, "r") as f:
                        content = f.read()
                        if "address:" in content.lower():
                            addr, priv = None, None
                            for line in content.split('\n'):
                                if "address:" in line.lower(): addr = line.split(":")[1].strip()
                                if "private key:" in line.lower(): priv = line.split(":")[1].strip()
                            if addr and priv:
                                try: os.remove(batch_path); os.remove(result_file)
                                except: pass
                                return addr, priv
                time.sleep(0.5)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Vast.ai / Linux multi-gpu high throughput pipe mode
            print(f"[*] Vast.ai Turbo Attack: T{prefix}...{suffix} (Streaming 2x RTX 4090 pipelines...)")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            start_t = time.time()

            addr, priv = None, None
            while time.time() - start_t < timeout:
                line = process.stdout.readline()
                if not line: break
                l_low = line.lower()
                if "address:" in l_low:
                    addr = line.split("address:")[1].strip()
                if "private key:" in l_low:
                    priv = line.split("private key:")[1].strip()

                if addr and priv:
                    process.terminate()
                    return addr, priv
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
                r.set(f"mine_status:{pattern}", "error")
                print(f"[❌] TIMEOUT.")
        except Exception as e:
            print(f"Queue error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    process_queue()
