# Tron Sentinel: USDT Monitoring & Vanity Engine

A lightweight, high-performance automated dashboard designed to track, isolate, and log transactional activity among TRC-20 USDT accounts on the TRON blockchain.

## 🚀 Architectural Overview

The system is split into two specialized tiers to ensure maximum efficiency:
- **The Brain (VPS Tier):** Handles ingestion, data filtering, and communication 24/7 on low-power cloud infrastructure.
- **The Muscle (GPU Tier):** Offloads heavy cryptographic verification to pay-as-you-go GPU nodes (NVIDIA RTX 4090) for on-demand vanity address generation.

## 🛠 Project Modules

### Module A: Directory Harvester
Scans the TRON blockchain for high-value USDT wallets (>= 7,499 USDT), extracts 4x5 character patterns, and stores them in Redis with a 24h TTL. Includes safety filters for ambiguous Base58 characters.

### Module B: gRPC Network Stream Listener (In Progress)
Intercepts live USDT transfers via low-latency gRPC streams, filtering for transactions within the 1-501 USDT range and matching them against the Redis index.

### Module C: Interactive Alert Interface (Planned)
Dispatches Markdown-formatted alerts to a secure Telegram Bot with inline "Vanity It!" action buttons.

### Module D: GPU Task Queue & Action Engine
Manages a FIFO queue in Redis for address generation tasks, triggering `profanity.exe` (OpenCL TRON Profanity Engine) to generate matching address layouts with **simultaneous Prefix + Suffix matching** in 8-15 seconds. See [GPU Engine Docs](docs/GPU_ENGINE.md).

## 📦 Setup Instructions

1. **Prerequisites:**
   - Python 3.10+
   - Redis Server
   - NVIDIA GPU with CUDA (for Module D)

2. **Installation:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration:**
   Create a `.env` file based on the template:
   ```env
   TRON_GRID_API_KEY=your_key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   USDT_CONTRACT=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
   MIN_USDT_BALANCE=7499
   ```

4. **Running the System:**
   You can use the main control script to manage the modules:
   ```bash
   # To start everything (Harvest then Monitor)
   python main.py start

   # To just harvest wallets
   python main.py harvest

   # To just monitor transactions
   python main.py monitor
   ```

## ⚖ License
Private Project - All Rights Reserved.
