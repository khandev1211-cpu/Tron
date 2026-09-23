# TRON Profanity GPU Vanity Engine Documentation

## 📌 Overview
TRON Sentinel utilizes a high-throughput OpenCL GPU binary engine (`profanity.exe`) to generate TRC-20 vanity addresses with **simultaneous Prefix and Suffix matching** on NVIDIA and AMD GPUs.

---

## 📂 Executable & Source Details
- **Executable Location:** `tools/profanity_windows/windows/profanity.exe`
- **Extracted From Archive:** `tools/repo_niocm/dist/windows.zip`
- **Architecture:** 64-bit Windows Native Executable (C++ OpenCL)
- **Primary GPU Target:** NVIDIA GeForce GTX 1660 SUPER (Tested locally) / RTX 4090

---

## ⚡ Simultaneous Prefix + Suffix Generation

Unlike basic generators that search only for a prefix OR a suffix sequentially, this engine searches for **BOTH** simultaneously in GPU memory.

### CLI Command Format
```cmd
"tools\profanity_windows\windows\profanity.exe" ^
  --matching <TARGET_34_CHAR_ADDRESS> ^
  --prefix-count <N> ^
  --suffix-count <M> ^
  --quit-count 1 ^
  --skip 1 ^
  --output <RESULT_FILE>
```

### Argument Breakdown
| Flag | Description | Example |
| :--- | :--- | :--- |
| `--matching` | Target 34-char Base58 TRON address string | `TLaGj00000000000000000000000GYitv` |
| `--prefix-count` | Number of characters to match at start (after leading 'T') | `3` (matches `LaG`) |
| `--suffix-count` | Number of characters to match at end | `3` (matches `itv`) |
| `--quit-count` | Stops GPU generation once `N` matches are found | `1` |
| `--skip` | Skips GPU device index (e.g. `1` to bypass integrated GPU) | `1` |
| `--output` | Output file path for CSV result (`privatekey,address`) | `result.txt` |

---

## 📊 Live System Benchmark Results

Tested on **NVIDIA GeForce GTX 1660 SUPER**:

| Precision | Target Pattern | Time Taken | Result Address Example |
| :--- | :--- | :--- | :--- |
| **2 + 2** | `TLa...tv` | **8.64 sec** | `TLKfWZdJHpvY3xKxHpVBmM31BHpaZ9Pbtv` |
| **3 + 3** | `TLau...itv` | **13.75 sec** | `TLaut1evj9J83eti9sm9odPoaNMzqcGitv` |

---

## ⚙️ Python Integration

The GPU engine is integrated into TRON Sentinel through two scripts:
1. `scripts/gpu_engine.py`: Triggered on demand via dashboard or CLI.
2. `scripts/gpu_worker.py`: Background Redis queue worker processing `gpu_queue` jobs.

### Configuration (`.env`)
```env
GPU_MINER_PATH=C:\Users\CHAND COMPUTER\Desktop\Tron\tools\profanity_windows\windows\profanity.exe
GPU_PREFIX_MATCH_LEN=3
GPU_SUFFIX_MATCH_LEN=3
GPU_MINING_TIMEOUT=120
```
