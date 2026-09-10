import os
import uvicorn
import json
import subprocess
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from base_agent import BaseAgent
from datetime import datetime
from gpu_engine import start_mining

class WebAgent(BaseAgent):
    def __init__(self):
        super().__init__("WebAgent")
        self.app = FastAPI(title="Tron Sentinel Dashboard")
        self.templates = Jinja2Templates(directory="templates")
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/")
        async def index(request: Request):
            target_keys = self.r.keys("target:*")
            targets_list = [json.loads(self.r.get(k)) for k in target_keys[:50] if self.r.get(k)]
            matches = [json.loads(m) for m in self.r.lrange("match_history", 0, 19)]

            return self.templates.TemplateResponse(
                request=request,
                name="dashboard.html",
                context={
                    "target_count": len(target_keys),
                    "targets": targets_list,
                    "matches": matches,
                    "filters": {
                        "min_val": os.getenv("BOT_FILTER_MIN_TRANSFER"),
                        "max_val": os.getenv("BOT_FILTER_MAX_TRANSFER"),
                        "min_bal": os.getenv("BOT_FILTER_MIN_BALANCE"),
                        "max_bal": os.getenv("BOT_FILTER_MAX_BALANCE")
                    },
                    "system_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )

        @self.app.post("/api/mine/{pattern}")
        async def trigger_mining(pattern: str):
            self.log(f"Manual Mining Triggered for pattern: {pattern}")
            success, msg = start_mining(pattern)
            return {"success": success, "message": msg}

        @self.app.post("/simulate")
        async def simulate():
            target_keys = self.r.keys("target:*")
            if not target_keys: return {"error": "No targets"}
            key = target_keys[0]
            data = json.loads(self.r.get(key))
            match_data = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "value": 250.75,
                "balance": data['balance'],
                "pattern": key.replace("target:", ""),
                "address": data['address']
            }
            self.r.lpush("match_history", json.dumps(match_data))
            self.r.ltrim("match_history", 0, 99)
            return {"status": "success"}

    def on_run(self):
        self.log("Starting Web Dashboard on http://0.0.0.0:8000")
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="warning")

if __name__ == "__main__":
    agent = WebAgent()
    agent.run()
