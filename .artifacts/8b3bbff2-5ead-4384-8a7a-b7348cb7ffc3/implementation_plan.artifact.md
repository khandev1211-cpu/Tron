# Distributed GPU Mining Setup (Local Dashboard + Vast.ai 2x 4090)

This plan outlines how to link your powerful Vast.ai instance (2x RTX 4090) to your local Sentinel Dashboard. This allows you to monitor targets locally while offloading the heavy mining work to the high-performance remote GPUs.

## User Review Required

> [!IMPORTANT]
> **Ngrok Requirement**: You will need to install [ngrok](https://ngrok.com/download) on your local Windows PC to create a secure tunnel for Redis. This is the simplest way to let Vast.ai "see" your local database without complex firewall rules.

> [!WARNING]
> **Redis Security**: When exposing Redis via ngrok, ensure you have a strong password set in your `.env` and `redis.conf` if possible, although for a temporary session, the unique ngrok URL provides obfuscation.

## Proposed Changes

### 1. Local Configuration (Windows)

We need to make the local Redis server accessible to the outside world so the Vast.ai worker can pick up tasks.

#### [MODIFY] [.env](file:///C:/Users/CHAND%20COMPUTER/Desktop/Tron/.env)
*   Add a `REDIS_PASSWORD` if not already present (optional but recommended).
*   Ensure `REDIS_PORT=6379`.

### 2. Vast.ai Configuration (Remote)

Setting up the "Action Engine" on the dual 4090 machine.

#### [NEW] [vast_setup.sh](file:///C:/Users/CHAND%20COMPUTER/Desktop/Tron/scripts/vast_setup.sh)
A specialized script for Vast.ai to install dependencies and configure the environment in one go.

#### [MODIFY] [gpu_worker.py](file:///C:/Users/CHAND%20COMPUTER/Desktop/Tron/scripts/gpu_worker.py)
*   Ensure the `get_redis_client` uses the external ngrok URL.
*   Confirm `devices: all` is utilized for both 4090s.

---

## Execution Steps

### Phase 1: Expose Local Redis
1.  Download and authenticate `ngrok`.
2.  Run the command: `ngrok tcp 6379`.
3.  Note the **Forwarding URL** (e.g., `tcp://0.tcp.ngrok.io:12345`).

### Phase 2: Prepare Vast.ai
1.  Connect to Vast.ai via SSH.
2.  Clone the project: `git clone https://github.com/khandev1211-cpu/Tron.git /workspace/Tron`.
3.  Navigate to the folder: `cd /workspace/Tron`.
4.  Run the setup script: `bash scripts/vast_setup.sh`.

### Phase 3: Connect the Node
1.  Edit `/workspace/Tron/.env` on Vast.ai:
    *   `REDIS_HOST`: Use the ngrok domain (e.g., `0.tcp.ngrok.io`).
    *   `REDIS_PORT`: Use the ngrok port (e.g., `12345`).
    *   `GPU_MINER_PATH=/workspace/provanity`.
2.  Start the worker: `python3 scripts/gpu_worker.py`.

## Verification Plan

### Automated Tests
*   **Heartbeat Check**: The local dashboard should display "2x RTX 4090 Active" once the worker connects to Redis.
*   **Mining Test**: Click "Vanity It!" on a local match and verify the Vast.ai terminal shows the mining process starting on both GPUs.

### Manual Verification
*   Verify the generated Private Key appears in the local dashboard after ~5-15 seconds.
