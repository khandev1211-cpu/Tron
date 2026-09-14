import time

def calculate_rtx_4090_limits():
    # Standard RTX 4090 speed for Vanity generation
    speed_per_sec = 6000000000 # 6 Billion Keys/sec
    target_time = 15 # Client's requirement

    total_combinations = speed_per_sec * target_time

    print("--- RTX 4090 POISONING OPTIMIZER ---")
    print(f"Target Time: {target_time} Seconds")
    print(f"Available Power: 6,000,000,000 keys/sec\n")

    # Tron uses Base58 (58 characters)
    # 58^x = total_combinations
    import math
    max_chars = math.log(total_combinations, 58)

    print(f"[*] Maximum Matching Characters in 15s: {round(max_chars, 1)}")
    print(f"[*] Recommended Pattern: 3 Prefix + 3 Suffix (Total 6 Chars)")

    print("\n--- TIME FOR CLIENT'S 10-CHAR (5+5) TARGET ---")
    comb_10 = 58**10
    time_sec = comb_10 / speed_per_sec
    print(f"[!] 10-char match would take: {round(time_sec / 86400 / 30, 1)} Months")

    print("\n--- STRATEGY FOR SUCCESS ---")
    print("To give the client results in 15 seconds, we must use a 'Dynamic Pattern':")
    print("1. Try 6 chars (3+3) -> Guaranteed in ~3-5 seconds.")
    print("2. Try 7 chars (4+3) -> Takes ~3 minutes.")

if __name__ == "__main__":
    calculate_rtx_4090_limits()
