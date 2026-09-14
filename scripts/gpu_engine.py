import os
import subprocess
import sys
import platform
import redis
import json
from dotenv import load_dotenv

load_dotenv()

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, protocol=2)

def is_gpu_available():
    try:
        subprocess.check_output(["nvidia-smi"], stderr=subprocess.STDOUT)
        return True
    except:
        return False

def start_mining(pattern):
    """
    Triggers the Poisoning Engine using NVIDIA GPU (ProVanity).
    Falls back to Python CPU if GPU is not available.
    """
    r.set(f"mine_status:{pattern}", "mining")

    python_miner = os.path.join(os.getcwd(), "scripts", "python_miner.py")
    gpu_miner_path = os.getenv("GPU_MINER_PATH")

    use_gpu = is_gpu_available() and gpu_miner_path and os.path.exists(gpu_miner_path)
    current_os = platform.system()

    try:
        if use_gpu:
            # ProVanity pattern logic:
            # If pattern is TLaGj*GYitv, we use prefix:LaGj (T is implicit)
            parts = pattern.split('*')
            prefix = parts[0]
            if prefix.startswith('T'):
                prefix = prefix[1:] # Strip leading T for ProVanity

            # Note: ProVanity v1.1.1 doesn't support combined prefix+suffix in a single flag easily
            # We target the prefix as the primary match
            cmd_pattern = f"prefix:{prefix}"

            if current_os == "Windows":
                # Launch ProVanity in a visible background window so the user can see the progress
                batch_content = f"""@echo off
title SENTINEL GPU ENGINE - {pattern}
echo [+] Starting NVIDIA GPU Attack for {pattern}
"{gpu_miner_path}" generate-tron --pattern {cmd_pattern} --devices 0
pause
"""
                batch_path = os.path.join(os.getcwd(), "run_gpu_attack.bat")
                with open(batch_path, "w") as f:
                    f.write(batch_content)

                subprocess.Popen(["cmd", "/c", "start", batch_path], shell=True)
            else:
                # Linux/VPS (nohup)
                cmd = f'nohup "{gpu_miner_path}" generate-tron --pattern {cmd_pattern} > vanity_{pattern}.log 2>&1 &'
                os.system(cmd)
            mode = "GPU (NVIDIA)"
        else:
            # CPU Fallback
            if current_os == "Windows":
                subprocess.Popen([sys.executable, python_miner, pattern],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                cmd = f'nohup {sys.executable} "{python_miner}" "{pattern}" > /dev/null 2>&1 &'
                os.system(cmd)
            mode = "CPU (Fallback)"

        r.set(f"mine_mode:{pattern}", mode)
        return True, f"Attack started via {mode}."
    except Exception as e:
        r.set(f"mine_status:{pattern}", "error")
        return False, f"Engine Error: {str(e)}"

if __name__ == "__main__":
    print(start_mining("TLaGj*GYitv"))
