import subprocess
import time
import os

def run_benchmark():
    gpu_path = r"C:\Users\CHAND COMPUTER\Desktop\Tron\tools\provanity.exe"
    pattern = "prefix:ABC"

    print(f"--- GPU PERFORMANCE BENCHMARK ---")
    print(f"GPU: NVIDIA GeForce GTX 1660 Ti")
    print(f"Target Pattern: {pattern} (3 chars)")
    print(f"Launching ProVanity...")

    start_time = time.time()
    try:
        # We need to run it in a way that captures the final result
        # ProVanity uses TUI/Refresh which might mess with capture_output
        process = subprocess.run(
            [gpu_path, "generate-tron", "--pattern", pattern, "--devices", "0"],
            capture_output=True,
            text=True,
            timeout=30
        )

        end_time = time.time()
        elapsed = end_time - start_time

        print(f"Output received. Elapsed: {round(elapsed, 2)}s")

        if "address:" in process.stdout:
            print(f"✅ SUCCESS! Match found.")
            for line in process.stdout.split('\n'):
                if "address:" in line or "private key:" in line or "attempts:" in line:
                    print(f"[*] {line.strip()}")
        else:
            print(f"❌ No match in output. Raw output length: {len(process.stdout)}")
            if len(process.stdout) < 100:
                print(f"Raw Output: {process.stdout}")
                print(f"Raw Error: {process.stderr}")

    except subprocess.TimeoutExpired:
        print("\n[!] 30 seconds passed. Something is wrong with the capture.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_benchmark()
