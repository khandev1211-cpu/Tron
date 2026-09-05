# Modules C & D: Alerting & Execution

## Module C: Telegram Interface
- **Messaging:** Sends Markdown alerts with transaction details and a block explorer link.
- **Interactivity:** Inline keyboard button "🛠️ Vanity It!" to trigger generation.
- **Security:** Strict user ID validation to prevent unauthorized commands.

## Module D: GPU Action Engine
- **Queue:** FIFO (First-In-First-Out) queue to prevent GPU thread collisions.
- **Hardware:** Optimized for NVIDIA RTX 4090.
- **Engine:** `tron-profanity-latest` (CUDA-based).
- **Performance:** Discover matching patterns in 2-15 seconds.
- **Delivery:** Delivers generated private key/address back to the Telegram channel.
