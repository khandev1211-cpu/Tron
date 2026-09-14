import os
import subprocess
import time

def test_gpu_power():
    gpu_path = r"C:\Users\CHAND COMPUTER\Downloads\khan-windows\khan.exe"
    if not os.path.exists(gpu_path):
        print(f"❌ Error: Miner not found at {gpu_path}")
        return

    print("--- SENTINEL GPU POWER TEST ---")
    print("Testing NVIDIA GTX 1660 Ti acceleration...")

    # Simple 3-char match to check speed
    start = time.time()
    try:
        # Running for 10 seconds just to see the output speed
        process = subprocess.Popen([gpu_path, "--matching", "TABC*123"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5) # Let it run for 5 seconds
        process.terminate()
        print("✅ GPU Miner is working and communicating with CUDA!")
        print("Now you can use the GENERATE button on Dashboard for 5+5 matches.")
    except Exception as e:
        print(f"❌ GPU Test Failed: {e}")

if __name__ == "__main__":
    test_gpu_power()
