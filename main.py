import os
import subprocess
import sys
import time

def run_harvester():
    print("\n[+] Starting Module A: Directory Harvester...")
    try:
        # Run harvester as a blocking process
        result = subprocess.run([sys.executable, "scripts/pre_gen.py"], check=True)
        print("[*] Harvester finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Harvester failed with error: {e}")

def run_monitor():
    print("\n[+] Starting Module B: Real-Time Stream Listener...")
    try:
        # Monitor runs indefinitely, so we use Popen or just call it if this is the last step
        subprocess.run([sys.executable, "scripts/monitor.py"], check=True)
    except KeyboardInterrupt:
        print("\n[*] Monitoring stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Monitor failed with error: {e}")

def main():
    print("========================================")
    print("       TRON SENTINEL CONTROL HUB        ")
    print("========================================\n")

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
    else:
        print("Available Commands:")
        print("  harvest  : Run the wallet harvester (Module A)")
        print("  monitor  : Run the live transaction listener (Module B)")
        print("  start    : Run harvest, then start monitor")
        print("  test     : Run tests to verify setup")
        cmd = input("\nEnter command: ").strip().lower()

    if cmd == "harvest":
        run_harvester()
    elif cmd == "monitor":
        run_monitor()
    elif cmd == "start":
        run_harvester()
        run_monitor()
    elif cmd == "test":
        print("\n[+] Running Tests...")
        subprocess.run([sys.executable, "tests/test_pre_gen.py"])
        subprocess.run([sys.executable, "tests/test_monitor.py"])
    else:
        print(f"[!] Unknown command: {cmd}")

if __name__ == "__main__":
    main()
