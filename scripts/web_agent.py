import os
import uvicorn
import json
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from base_agent import BaseAgent
from datetime import datetime

class WebAgent(BaseAgent):
    def __init__(self):
        super().__init__("WebAgent")
        self.app = FastAPI(title="Tron Sentinel Dashboard")
        self.templates = Jinja2Templates(directory="templates")
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/")
        async def index(request: Request):
            # Fetch stats from Redis
            target_keys = self.r.keys("target:*")

            # Fetch harvested targets list
            targets_list = []
            for key in target_keys[:50]:
                raw = self.r.get(key)
                if raw:
                    try:
                        targets_list.append(json.loads(raw))
                    except:
                        pass

            matches = self.r.lrange("match_history", 0, 19) # Last 20 matches

            match_list = []
            for m in matches:
                try:
                    match_list.append(json.loads(m))
                except:
                    pass

            return self.templates.TemplateResponse(
                request=request,
                name="dashboard.html",
                context={
                    "target_count": len(target_keys),
                    "targets": targets_list,
                    "matches": match_list,
                    "system_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )

        @self.app.get("/api/status")
        async def get_status():
            return {
                "status": "online",
                "redis": self.check_health(),
                "targets": len(self.r.keys("target:*")),
                "last_update": datetime.now().isoformat()
            }

    def on_run(self):
        self.log("Starting Web Dashboard on http://0.0.0.0:8000")
        # uvicorn.run is blocking
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="warning")

if __name__ == "__main__":
    agent = WebAgent()
    agent.run()
