import os
import sys
import time
import requests
import json
from decimal import Decimal
from datetime import datetime
from base_agent import BaseAgent

class BackfillAgent(BaseAgent):
    def __init__(self):
        super().__init__("BackfillAgent")
        self.usdt_contract = os.getenv("USDT_CONTRACT", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
        self.trongrid_key = os.getenv("TRON_GRID_API_KEY")

        # Ranges
        self.bot_min_val = Decimal(os.getenv("BOT_FILTER_MIN_TRANSFER", "0.1"))
        self.bot_max_val = Decimal(os.getenv("BOT_FILTER_MAX_TRANSFER", "1000000"))
        self.bot_min_bal = Decimal(os.getenv("BOT_FILTER_MIN_BALANCE", "1000"))
        self.bot_max_bal = Decimal(os.getenv("BOT_FILTER_MAX_BALANCE", "1000000000"))

    def get_pattern(self, address):
        # Module 4: Address Poisoning Pattern (1st 5 and Last 5)
        return f"{address[:5]}*{address[-5:]}"

    def check_target_history(self, address, holder_bal):
        # Use TRC20 specific transaction endpoint
        url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
        params = {
            "limit": 5,
            "contract_address": self.usdt_contract,
            "only_confirmed": True
        }
        headers = {"User-Agent": "TronSentinel/1.0", "Origin": "https://api.trongrid.io/get"}
        if self.trongrid_key: headers["TRON-PRO-API-KEY"] = self.trongrid_key

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                transactions = resp.json().get('data', [])
                for tx in transactions:
                    # Check if it was an outgoing transfer from our target
                    if tx.get('from') == address:
                        value = Decimal(tx.get('value', '0')) / Decimal(10**tx.get('token_info', {}).get('decimals', 6))

                        if self.bot_min_val <= value <= self.bot_max_val:
                            pattern = self.get_pattern(address)
                            tx_time = datetime.fromtimestamp(tx.get('block_timestamp')/1000).strftime("%H:%M:%S")

                            match_data = {
                                "time": tx_time,
                                "value": float(value),
                                "balance": float(holder_bal),
                                "pattern": pattern,
                                "address": address,
                                "tx_id": tx.get('transaction_id')
                            }

                            # Check for duplicates in Redis history
                            history = self.r.lrange("match_history", 0, -1)
                            is_dup = any(json.loads(m).get('tx_id') == match_data['tx_id'] or
                                        (json.loads(m)['time'] == tx_time and json.loads(m)['address'] == address)
                                        for m in history)

                            if not is_dup:
                                self.log(f"!!! REAL HISTORY MATCH: {address} | {value} USDT", "info")
                                self.r.lpush("match_history", json.dumps(match_data))
                                self.r.ltrim("match_history", 0, 99)
        except Exception as e:
            # self.log(f"Scan error for {address}: {e}", "warning")
            pass

    def on_run(self):
        self.log("Starting Real History Sweep for all targets...")
        target_keys = self.r.keys("target:*")
        self.log(f"Analyzing {len(target_keys)} target wallets for recent activity...")

        count = 0
        for key in target_keys:
            raw = self.r.get(key)
            if raw:
                try:
                    data = json.loads(raw)
                    self.check_target_history(data['address'], data['balance'])
                    count += 1
                    # Log progress every 50 wallets
                    if count % 50 == 0:
                        self.log(f"Sweep Progress: {count}/{len(target_keys)} wallets analyzed.")
                    time.sleep(0.5) # Prevent rate limits
                except:
                    pass

        self.log("Sweep completed. All target histories are up to date.")
        self.log("Sleeping for 5 minutes before next sweep...")
        for _ in range(300):
            if not self.is_running: break
            time.sleep(1)

if __name__ == "__main__":
    agent = BackfillAgent()
    agent.run()
