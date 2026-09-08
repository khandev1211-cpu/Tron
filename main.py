import os
import subprocess
import sys
import time

def run_agent():
    print("\n[+] Launching Sentinel Master Agent...")
    try:
        subprocess.run([sys.executable, "agent_system.py"], check=True)
    except KeyboardInterrupt:
        print("\n[*] Sentinel stopped.")
    except Exception as e:
        print(f"[!] Error: {e}")

def main():
    print("========================================")
    print("       TRON SENTINEL CONTROL HUB        ")
    print("========================================\n")

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
    else:
        print("Available Commands:")
        print("  agent    : Start the Master Agent (Self-healing VPS mode)")
        print("  harvest  : Run the Harvester Sub-Agent once")
        print("  test     : Run project test suite")
        cmd = input("\nEnter command: ").strip().lower()

    if cmd == "agent":
        run_agent()
    elif cmd == "harvest":
        subprocess.run([sys.executable, "scripts/harvester_agent.py"])
    elif cmd == "test":
        print("\n[+] Running Tests...")
        subprocess.run([sys.executable, "tests/test_monitor.py"])
    else:
        print(f"[!] Unknown command: {cmd}")

if __name__ == "__main__":
    main()
