# Modules C & D: Alerting & Execution

## Module C: Telegram Interface
- **Messaging:** Sends Markdown alerts with transaction details and a block explorer link.
- **Interactivity:** Inline keyboard button "🛠️ Vanity It!" to trigger generation.
- **Security:** Strict user ID validation to prevent unauthorized commands.

## Module D: GPU Action Engine
- **Queue:** FIFO (First-In-First-Out) queue in Redis (`gpu_queue`) to prevent GPU thread collisions.
- **Engine Executable:** `tools/profanity_windows/windows/profanity.exe` (OpenCL TRON Profanity Generator).
- **Features:** Supports **simultaneous Prefix + Suffix matching** in a single GPU pass.
- **Hardware:** Tested on NVIDIA GTX 1660 SUPER / RTX 4090.
- **Performance:** Matches 3+3 prefix/suffix patterns in ~13 seconds.
- **Output:** Saves generated Base58 Address and Private Key directly to CSV result files.
- **Detailed Guide:** See [GPU Engine Documentation](GPU_ENGINE.md) for full CLI flags, benchmarks, and configuration.
