import os
import requests
import json
import time
from decimal import Decimal
from base_agent import BaseAgent

class HarvesterAgent(BaseAgent):
    def __init__(self):
        super().__init__("HarvesterAgent")
        self.usdt_contract = os.getenv("USDT_CONTRACT", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
        self.min_balance = Decimal(os.getenv("MIN_USDT_BALANCE", "7499"))
        self.redis_ttl = int(os.getenv("REDIS_TTL", 86400))
        self.exclusion_chars = {'0', 'O', 'I', 'l'}

        self.tronscan_key = os.getenv("TRONSCAN_API_KEY")
        self.trongrid_key = os.getenv("TRON_GRID_API_KEY")

    def is_valid_pattern(self, address):
        if not address or len(address) < 10: return False
        pattern_parts = address[1:5] + address[-5:]
        return not any(char in self.exclusion_chars for char in pattern_parts)

    def get_pattern(self, address):
        return f"{address[1:5]}*{address[-5:]}"

    def fetch_holders(self):
        url = "https://apilist.tronscanapi.com/api/token_trc20/holders"
        params = {
            "contract_address": self.usdt_contract,
            "start": 0, "limit": 500, "sort": "balance"
        }
        headers = {
            "User-Agent": "TronSentinel/1.0",
            "Origin": "https://api.trongrid.io/get"
        }

        api_key = self.tronscan_key if self.tronscan_key and "PASTE" not in self.tronscan_key else self.trongrid_key
        if api_key: headers["TRON-PRO-API-KEY"] = api_key

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json().get("trc20_tokens", [])
        except Exception as e:
            self.log(f"Fetch failed: {e}", "error")
            return []

    def on_run(self):
        self.log("Starting production harvest (Top 50 High-Value Wallets)...")

        all_holders = []
        # Fetching Top 50 holders as requested
        url = "https://apilist.tronscanapi.com/api/token_trc20/holders"
        params = {
            "contract_address": self.usdt_contract,
            "start": 0, "limit": 50, "sort": "balance"
        }
        headers = {"User-Agent": "TronSentinel/1.0", "Origin": "https://api.trongrid.io/get"}
        api_key = self.tronscan_key if self.tronscan_key and "PASTE" not in self.tronscan_key else self.trongrid_key
        if api_key: headers["TRON-PRO-API-KEY"] = api_key

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            all_holders = response.json().get("trc20_tokens", [])
        except Exception as e:
            self.log(f"Fetch failed: {e}", "error")

        self.log(f"Total potential holders fetched: {len(all_holders)}")

        count = 0
        pipe = self.r.pipeline()
        for holder in all_holders:
            address = holder.get("holder_address")
            if not address: continue

            balance = Decimal(holder.get("balance", "0")) / Decimal(10**6)
            # Production filter: balance >= 7,499 USDT
            if balance >= self.min_balance and self.is_valid_pattern(address):
                pattern = self.get_pattern(address)
                redis_key = f"target:{pattern}"
                data = {"address": address, "balance": float(balance)}
                pipe.set(redis_key, json.dumps(data), ex=self.redis_ttl)
                count += 1

        pipe.execute()
        self.log(f"Successfully harvested {count} high-value patterns into Redis.")
        self.is_running = False

if __name__ == "__main__":
    agent = HarvesterAgent()
    agent.run()
