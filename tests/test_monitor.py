import unittest
from decimal import Decimal
from unittest.mock import MagicMock
import sys
import os

# Add scripts to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from monitor import process_event, get_pattern

class TestMonitor(unittest.TestCase):
    def setUp(self):
        self.mock_redis = MagicMock()

    def test_pattern_match_success(self):
        # Setup mock Redis to return True for a specific pattern
        target_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        pattern = get_pattern(target_address)
        self.mock_redis.exists.side_effect = lambda k: k == f"target:{pattern}"

        # Mock event
        event = {
            'result': {
                'from': target_address,
                'to': 'TReceiverAddress1234567890',
                'value': '100000000' # 100 USDT
            },
            'timestamp': 123456789
        }

        # We check console output manually or just verify it doesn't crash
        # and calls redis.exists
        process_event(self.mock_redis, event)
        self.mock_redis.exists.assert_called_with(f"target:{pattern}")

    def test_threshold_filtering(self):
        # 0.5 USDT (Below threshold)
        event_low = {'result': {'from': 'S', 'to': 'R', 'value': '500000'}}
        # 1000 USDT (Above threshold)
        event_high = {'result': {'from': 'S', 'to': 'R', 'value': '1000000000'}}

        process_event(self.mock_redis, event_low)
        process_event(self.mock_redis, event_high)

        # Should not call redis.exists for these
        self.mock_redis.exists.assert_not_called()

if __name__ == "__main__":
    unittest.main()
