# Module A: Directory Harvester

## Purpose
The Harvester is responsible for identifying "targets" (high-balance USDT wallets) and preparing their address patterns for fast lookup.

## Core Logic
1. **Fetch Holders:** Uses TronScan API to get top USDT holders.
2. **Filter Balance:** Only considers wallets with $\ge$ 7,499 USDT.
3. **Trait Extraction:** 
   - Takes the first 4 characters (after 'T').
   - Takes the last 5 characters.
   - Example: `TR7NH...Lj6t` $\rightarrow$ `R7NH*Lj6t`.
4. **Safety Check:** Skips patterns containing `0`, `O`, `I`, `l` to avoid hardware bottlenecks.
5. **Storage:** Injects patterns into Redis as keys (`target:<pattern>`) with a 24-hour expiration.

## Usage
Run the script periodically (e.g., via cron) to keep the target list fresh.
```bash
python scripts/pre_gen.py
```
