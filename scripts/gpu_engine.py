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
    Triggers the Poisoning Engine using NVIDIA GPU (TRON Profanity Engine).
    Generates combined prefix and suffix simultaneously.
    Falls back to Python CPU if GPU is not available.
    """
    r.set(f"mine_status:{pattern}", "mining")

    python_miner = os.path.join(os.getcwd(), "scripts", "python_miner.py")
    gpu_miner_path = os.getenv("GPU_MINER_PATH")

    use_gpu = is_gpu_available() and gpu_miner_path and os.path.exists(gpu_miner_path)
    current_os = platform.system()

    try:
        if use_gpu:
            # Parse pattern (e.g. TLaGj*GYitv or TLaGj...GYitv)
            if '*' in pattern:
                parts = pattern.split('*')
            elif '...' in pattern:
                parts = pattern.split('...')
            else:
                parts = [pattern[:5], pattern[-5:]]

            prefix = parts[0][1:] if parts[0].startswith('T') else parts[0]
            suffix = parts[1]

            prefix_count = len(prefix)
            suffix_count = len(suffix)

            # Base58 valid padding template (34 total chars)
            base58_pad = "123456789ABCDEFGHJKLMNPQRSTUV"
            pad_needed = 34 - 1 - len(prefix) - len(suffix)
            dummy_fill = base58_pad[:pad_needed]
            target_address = f'T{prefix}{dummy_fill}{suffix}'

            result_file = os.path.join(os.getcwd(), f"result_{pattern.replace('*', '_')}.txt")

            if current_os == "Windows":
                # Launch TRON Profanity Engine in a visible background batch window
                batch_content = f"""@echo off
title SENTINEL GPU ENGINE - {pattern}
echo [+] Starting Simultaneous Prefix+Suffix NVIDIA GPU Attack for {pattern}
echo [+] Prefix: T{prefix} ({prefix_count} chars) | Suffix: {suffix} ({suffix_count} chars)
"{gpu_miner_path}" --matching {target_address} --prefix-count {prefix_count} --suffix-count {suffix_count} --quit-count 1 --skip 1 --output "{result_file}"
pause
"""
                batch_path = os.path.join(os.getcwd(), "run_gpu_attack.bat")
                with open(batch_path, "w") as f:
                    f.write(batch_content)

                subprocess.Popen(["cmd", "/c", "start", batch_path], shell=True)
            else:
                # Linux / VPS background mode
                cmd = f'nohup "{gpu_miner_path}" --matching {target_address} --prefix-count {prefix_count} --suffix-count {suffix_count} --quit-count 1 --output "{result_file}" > vanity_{pattern}.log 2>&1 &'
                os.system(cmd)
            mode = "GPU (NVIDIA Profanity - Combined Prefix+Suffix)"
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
