import unittest
from decimal import Decimal
from unittest.mock import MagicMock
import sys
import os
import json

# Add scripts to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from monitor_agent import MonitorAgent

class TestMonitor(unittest.TestCase):
    def setUp(self):
        # Create agent without starting it
        self.agent = MonitorAgent()
        self.agent.r = MagicMock()

    def test_pattern_match_success(self):
        target_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        pattern = self.agent.get_pattern(target_address)
        data = {"address": target_address, "balance": 10000.0}

        self.agent.r.get.side_effect = lambda k: json.dumps(data) if k == f"target:{pattern}" else None

        event = {
            'result': {
                'from': target_address,
                'to': 'TReceiverAddress1234567890',
                'value': '250000000'
            },
            'block_timestamp': 123456789
        }

        self.agent.process_event(event)
        self.agent.r.get.assert_called_with(f"target:{pattern}")

    def test_threshold_filtering(self):
        # 100 USDT (Below bot filter 200, but inside engine 1-501)
        event_low = {'result': {'from': 'S', 'to': 'R', 'value': '100000000'}}
        self.agent.r.get.return_value = None
        self.agent.process_event(event_low)
        # Should check Redis because it's within engine range
        self.assertTrue(self.agent.r.get.called)

if __name__ == "__main__":
    unittest.main()
