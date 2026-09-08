import os
import sys
import time
import logging
import redis
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.is_running = True

        # Ensure UTF-8 output for Windows console
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass

        self.setup_logging()

        # Redis Configuration
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.r = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            decode_responses=True,
            protocol=2
        )

    def setup_logging(self):
        log_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            level=logging.INFO,
            format=f'[%(asctime)s] [{self.agent_name}] %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, f"{self.agent_name.lower()}.log"), encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.agent_name)

    def log(self, message, level="info"):
        if level == "info": self.logger.info(message)
        elif level == "warning": self.logger.warning(message)
        elif level == "error": self.logger.error(message)

    def check_health(self):
        """Standard health check for all agents."""
        try:
            self.r.ping()
            return True
        except redis.ConnectionError:
            self.log("Redis connection lost!", "error")
            return False

    def on_start(self):
        """Override this method for initialization logic."""
        self.log(f"Agent {self.agent_name} starting...")

    def on_run(self):
        """Override this method for the main execution loop."""
        pass

    def on_shutdown(self):
        """Override this method for cleanup logic."""
        self.log(f"Agent {self.agent_name} shutting down...")

    def run(self):
        try:
            self.on_start()
            while self.is_running:
                if not self.check_health():
                    time.sleep(5)
                    continue
                self.on_run()
        except KeyboardInterrupt:
            self.on_shutdown()
        except Exception as e:
            self.log(f"Agent CRASHED: {e}", "error")
            self.on_shutdown()
            sys.exit(1)
