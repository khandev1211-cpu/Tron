import subprocess
import time
import os

def run_test():
    gpu_path = r"C:\Users\CHAND COMPUTER\Desktop\Tron\tools\provanity.exe"
    # Testing 5 chars: T + ABCDE
    # On 1660 Ti this should take ~5-15 seconds
    pattern = "prefix:ABCDE"

    print(f"--- REAL GPU TEST (5 CHARS) ---")
    print(f"Target: {pattern}")
    print(f"Hardware: NVIDIA GeForce GTX 1660 Ti")

    start_time = time.time()

    # We use 'cmd /c start /wait' to launch in a new window and wait for completion
    # This avoids the 'interactive terminal' error in the background
    cmd = f'start /wait "" "{gpu_path}" generate-tron --pattern {pattern} --devices 0'

    print("Launching GPU window... Please wait for it to close automatically.")
    subprocess.call(cmd, shell=True)

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n✅ TEST COMPLETED!")
    print(f"Time Taken for 5-char match: {round(elapsed, 2)} seconds")

    # RTX 4090 is ~15x faster than 1660 Ti
    rtx_4090_est = elapsed / 15
    print(f"Estimated time on Client's RTX 4090: {round(rtx_4090_est, 2)} seconds")

    print("\n--- PERFORMANCE SCALING (RTX 4090) ---")
    print(f"6 Chars (3+3): ~{round(rtx_4090_est * 58 / 60, 2)} minutes")
    print(f"7 Chars (4+3): ~{round(rtx_4090_est * (58**2) / 3600, 2)} hours")
    print(f"8 Chars (4+4): ~{round(rtx_4090_est * (58**3) / 86400, 2)} days")

if __name__ == "__main__":
    run_test()
