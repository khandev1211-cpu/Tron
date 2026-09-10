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

        # Bot Filters (Wide for testing, tight for production)
        self.bot_min_val = Decimal(os.getenv("BOT_FILTER_MIN_TRANSFER", "0.1"))
        self.bot_max_val = Decimal(os.getenv("BOT_FILTER_MAX_TRANSFER", "1000000"))
        self.bot_min_bal = Decimal(os.getenv("BOT_FILTER_MIN_BALANCE", "1000"))
        self.bot_max_bal = Decimal(os.getenv("BOT_FILTER_MAX_BALANCE", "1000000000"))

        self.trongrid_key = os.getenv("TRON_GRID_API_KEY")
        self.since_timestamp = 0
        self.last_heartbeat = time.time()
        self.total_processed = 0

    def sync_with_blockchain_time(self):
        url = "https://api.trongrid.io/wallet/getnowblock"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            self.since_timestamp = data['block_header']['raw_data']['timestamp']
            self.log(f"Synced with Blockchain Time: {datetime.fromtimestamp(self.since_timestamp/1000)}")
            return True
        except Exception as e:
            self.log(f"Failed to sync time: {e}", "warning")
            return False

    def get_pattern(self, address):
        return f"{address[1:5]}*{address[-5:]}"

    def process_event(self, event):
        try:
            res = event.get('result', {})
            sender = res.get('from')
            value = Decimal(res.get('value', '0')) / Decimal(10**6)

            if not sender: return

            # Update Raw Feed in Redis (Latest 5 USDT transfers on network)
            raw_data = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "value": float(value),
                "from": sender[:10] + "..."
            }
            self.r.lpush("raw_transfers", json.dumps(raw_data))
            self.r.ltrim("raw_transfers", 0, 4)
            self.r.incr("stats:total_scanned")

            # Pattern Matching
            pattern = self.get_pattern(sender)
            target_raw = self.r.get(f"target:{pattern}")

            if target_raw:
                target = json.loads(target_raw)
                holder_bal = Decimal(str(target.get('balance', 0)))

                if (self.bot_min_val <= value <= self.bot_max_val) and \
                   (self.bot_min_bal <= holder_bal <= self.bot_max_bal):

                    match_data = {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "value": float(value),
                        "balance": float(holder_bal),
                        "pattern": pattern,
                        "address": sender
                    }
                    self.log(f"MATCH FOUND: {sender} | {value} USDT")
                    self.r.lpush("match_history", json.dumps(match_data))
                    self.r.ltrim("match_history", 0, 99)
                    send_alert(f"Match: {value} USDT from {sender}", pattern)
        except Exception as e:
            self.log(f"Event Error: {e}", "error")

    def on_run(self):
        if self.since_timestamp == 0:
            if not self.sync_with_blockchain_time():
                time.sleep(5)
                return

        if time.time() - self.last_heartbeat > 60:
            self.log(f"Scanning... Total Processed: {self.total_processed}")
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
            resp = requests.get(url, headers=headers, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            events = data.get('data', [])

            if events:
                self.total_processed += len(events)
                for event in events:
                    self.process_event(event)
                    self.since_timestamp = event['block_timestamp'] + 1
            else:
                time.sleep(2)

        except Exception as e:
            self.log(f"Sync Error: {e}", "warning")
            time.sleep(5)

if __name__ == "__main__":
    agent = MonitorAgent()
    agent.run()
