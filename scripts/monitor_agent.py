import os
import time
import requests
import json
from decimal import Decimal
from datetime import datetime
from base_agent import BaseAgent
from telegram_bot import send_alert

class MonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__("MonitorAgent")
        self.usdt_contract = os.getenv("USDT_CONTRACT", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
        self.min_engine = Decimal(os.getenv("MIN_TRANSFER_THRESHOLD", "1"))
        self.max_engine = Decimal(os.getenv("MAX_TRANSFER_THRESHOLD", "501"))

        # Bot Filters
        self.bot_min_val = Decimal(os.getenv("BOT_FILTER_MIN_TRANSFER", "200"))
        self.bot_max_val = Decimal(os.getenv("BOT_FILTER_MAX_TRANSFER", "300"))
        self.bot_min_bal = Decimal(os.getenv("BOT_FILTER_MIN_BALANCE", "9800"))
        self.bot_max_bal = Decimal(os.getenv("BOT_FILTER_MAX_BALANCE", "18500"))

        self.trongrid_key = os.getenv("TRON_GRID_API_KEY")

        # Start from current time to avoid syncing years of history
        self.since_timestamp = int(time.time() * 1000)
        self.last_heartbeat = time.time()
        self.consecutive_errors = 0

    def get_pattern(self, address):
        return f"{address[1:5]}*{address[-5:]}"

    def process_event(self, event):
        try:
            res = event.get('result', {})
            sender = res.get('from')
            receiver = res.get('to')
            value = Decimal(res.get('value', '0')) / Decimal(10**6)

            if not sender or not receiver: return

            if self.min_engine <= value <= self.max_engine:
                pattern = self.get_pattern(sender)
                raw_data = self.r.get(f"target:{pattern}")

                if raw_data:
                    target = json.loads(raw_data)
                    holder_bal = Decimal(str(target.get('balance', 0)))

                    if (self.bot_min_val <= value <= self.bot_max_val) and \
                       (self.bot_min_bal <= holder_bal <= self.bot_max_bal):

                        alert = (f"Match Found\n\n"
                                 f"Value: `{value}` USDT\n"
                                 f"Balance: `{holder_bal}` USDT\n"
                                 f"From: `{sender}`\n"
                                 f"Pattern: `{pattern}`")
                        self.log(f"ALERT: Match Found for {sender} ({value} USDT)")

                        # Store in Redis history for Dashboard
                        match_data = {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "value": float(value),
                            "balance": float(holder_bal),
                            "pattern": pattern,
                            "address": sender
                        }
                        self.r.lpush("match_history", json.dumps(match_data))
                        self.r.ltrim("match_history", 0, 99) # Keep last 100 matches

                        send_alert(alert, pattern)
        except Exception as e:
            self.log(f"Event Error: {e}", "error")

    def on_run(self):
        if time.time() - self.last_heartbeat > 60:
            self.log(f"Sentinel Monitor heartbeat active. Syncing from: {self.since_timestamp}")
            self.last_heartbeat = time.time()

        url = f"https://api.trongrid.io/v1/contracts/{self.usdt_contract}/events"
        params = {
            "event_name": "Transfer",
            "order_by": "timestamp,asc",
            "since_timestamp": self.since_timestamp,
            "limit": 50
        }
        headers = {"User-Agent": "TronSentinel/1.0", "Origin": "https://api.trongrid.io/get"}
        if self.trongrid_key: headers["TRON-PRO-API-KEY"] = self.trongrid_key

        try:
            # Increased timeout to 30s to handle network spikes
            resp = requests.get(url, headers=headers, params=params, timeout=30)

            if resp.status_code == 401:
                self.log("API Key Unauthorized (401). Using public tier.", "warning")
                if "TRON-PRO-API-KEY" in headers: del headers["TRON-PRO-API-KEY"]
                return

            resp.raise_for_status()
            events_data = resp.json()
            events = events_data.get('data', [])

            if events:
                self.log(f"Processing {len(events)} events...")
                for event in events:
                    self.process_event(event)
                    # Update timestamp to the latest event processed
                    self.since_timestamp = event['block_timestamp'] + 1
                self.consecutive_errors = 0

            time.sleep(1) # Small sleep to be polite

        except requests.exceptions.Timeout:
            self.log("Network timeout. Retrying...", "warning")
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            self.log("Connection error (DNS/Internet). Checking connectivity...", "error")
            time.sleep(5)
        except Exception as e:
            self.log(f"Listener Error: {e}", "error")
            self.consecutive_errors += 1
            if self.consecutive_errors > 5:
                # If stuck, reset to current time
                self.log("Too many errors. Resetting sync to current time.", "warning")
                self.since_timestamp = int(time.time() * 1000)
                self.consecutive_errors = 0
            time.sleep(5)

if __name__ == "__main__":
    agent = MonitorAgent()
    agent.run()
