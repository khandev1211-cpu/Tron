import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

MINER_PATH = os.getenv("GPU_MINER_PATH")

def start_mining(pattern):
    """
    Triggers the GPU mining process using tron-profanity.
    """
    # 1. Validation
    if not MINER_PATH:
        return False, "GPU_MINER_PATH not set in .env"

    executable = MINER_PATH if os.path.isabs(MINER_PATH) else os.path.join(os.getcwd(), MINER_PATH)

    if not os.path.exists(executable):
        return False, f"Miner executable not found at: {executable}"

    # 2. Pattern Parsing
    # Pattern: R7NH*jLj6t -> prefix R7NH, suffix jLj6t
    parts = pattern.split('*')
    prefix = parts[0]
    suffix = parts[1] if len(parts) > 1 else ""

    # 3. Execution Logic
    # We use a batch file to keep the window open after mining finishes for visibility
    batch_content = f"""@echo off
title Tron Sentinel GPU Miner - {pattern}
echo [+] Starting Mining for Pattern: {pattern}
echo [+] Using Miner: {executable}
"{executable}" --prefix {prefix} --suffix {suffix} --output vanity_results.txt
echo.
echo [+] Mining process finished. Results saved to vanity_results.txt
pause
"""
    batch_path = os.path.join(os.getcwd(), "start_mining.bat")
    with open(batch_path, "w") as f:
        f.write(batch_content)

    try:
        # Launching the batch file in a new console
        subprocess.Popen(["cmd", "/c", "start", batch_path], shell=True)
        return True, "GPU Miner launched in a new window."
    except Exception as e:
        return False, f"Process Error: {str(e)}"

if __name__ == "__main__":
    # Test call
    res, msg = start_mining("R7NH*jLj6t")
    print(msg)
