import os
import sys
import time
import subprocess
import redis
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), "scripts"))
def send_system_report(x):
    print(f"[System Report] {x}")

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
GPU_MINER_PATH = os.getenv("GPU_MINER_PATH")
HARVEST_INTERVAL = 6 * 3600  # 6 hours

class SentinelMasterAgent:
    def __init__(self):
        self.web_agent = None
        self.monitor_agent = None
        self.backfill_agent = None
        self.last_harvest = 0
        self.is_running = True
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, protocol=2)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [MASTER-AGENT] {message}")

    def check_redis(self):
        try:
            self.r.ping()
            return True
        except redis.ConnectionError:
            return False

    def run_sub_agent(self, script_name, args=None):
        script_path = os.path.join("scripts", script_name)
        cmd = [sys.executable, script_path] + (args or [])
        return subprocess.Popen(cmd)

    def orchestrate(self):
        # 1. Maintain Web Dashboard Sub-Agent
        if self.web_agent is None or self.web_agent.poll() is not None:
            self.web_agent = self.run_sub_agent("web_agent.py")
            self.log("Web Sub-Agent (Dashboard) synchronized.")

        # 2. Maintain Monitor Sub-Agent (Live Stream)
        if self.monitor_agent is None or self.monitor_agent.poll() is not None:
            self.monitor_agent = self.run_sub_agent("monitor_agent.py")
            self.log("Monitor Sub-Agent synchronized.")

        # 3. Maintain Backfill Sub-Agent (Account History Layer)
        if self.backfill_agent is None or self.backfill_agent.poll() is not None:
            self.backfill_agent = self.run_sub_agent("backfill_agent.py")
            self.log("Backfill Sub-Agent (History Scanner) synchronized.")

        # 4. Maintain GPU Worker Engine (Only run locally if local GPU binary path is defined & exists)
        if GPU_MINER_PATH and os.path.exists(GPU_MINER_PATH):
            if not hasattr(self, 'gpu_worker') or self.gpu_worker is None or self.gpu_worker.poll() is not None:
                self.gpu_worker = self.run_sub_agent("gpu_worker.py")
                self.log("Local GPU Worker Engine synchronized.")

    def start(self):
        self.log("========================================")
        self.log("   SENTINEL MASTER AGENT STARTING...    ")
        self.log("========================================")

        self.log("Master Agent active. Dashboard at http://localhost:8000")

        # Initial Harvest
        self.log("Performing initial harvest...")
        subprocess.run([sys.executable, os.path.join("scripts", "harvester_agent.py")])
        self.last_harvest = time.time()

        while self.is_running:
            try:
                if not self.check_redis():
                    self.log("CRITICAL: Redis connection failed.")
                    time.sleep(10)
                    continue

                self.orchestrate()

                if time.time() - self.last_harvest > HARVEST_INTERVAL:
                    self.log("Triggering scheduled harvest sub-agent...")
                    subprocess.Popen([sys.executable, os.path.join("scripts", "harvester_agent.py")])
                    self.last_harvest = time.time()

                time.sleep(5)
            except KeyboardInterrupt:
                self.log("Master Agent shutting down.")
                if self.monitor_agent: self.monitor_agent.terminate()
                if self.web_agent: self.web_agent.terminate()
                if self.backfill_agent: self.backfill_agent.terminate()
                self.is_running = False
            except Exception as e:
                self.log(f"Orchestrator Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    master = SentinelMasterAgent()
    master.start()
