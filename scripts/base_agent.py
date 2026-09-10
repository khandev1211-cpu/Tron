import os
import sys
import logging
import redis
import json

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

        # Connect to Redis with protocol=2 for backward compatibility
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.r = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            protocol=2
        )

    def setup_logging(self):
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, f"{self.agent_name.lower()}.log")

        # Configure logging to file (UTF-8) and console
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.agent_name)

    def log(self, message, level="info"):
        # Clean emojis for console stability if needed
        safe_msg = message.encode('ascii', 'ignore').decode('ascii')
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)

    def check_health(self):
        try:
            return self.r.ping()
        except:
            return False

    def run(self):
        self.log(f"Agent {self.agent_name} starting...")
        try:
            while self.is_running:
                self.on_run()
        except KeyboardInterrupt:
            self.log(f"Agent {self.agent_name} stopped.")
        except Exception as e:
            self.log(f"Agent Crash: {e}", "error")

    def on_run(self):
        raise NotImplementedError("Subclasses must implement on_run")
