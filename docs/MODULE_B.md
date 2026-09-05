# Module B: gRPC Stream Listener

## Purpose
Continuous interception of live transaction events to detect potential matches in real-time.

## Functional Requirements
- **Protocol:** gRPC (via TronGrid or private node).
- **Contract:** Monitors `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t` (USDT).
- **Filtering:** 
  - Captures `Transfer` events.
  - Value range: 1 to 501 USDT.
- **Matching:** Cross-references the `sender` address pattern against the Redis RAM cache in < 1ms.

## Technical Stack
- `tronpy` or `grpcio` for node connection.
- `redis-py` for lookup.
