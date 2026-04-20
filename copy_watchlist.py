import os
import shutil

# --- Paths ---
ARCH_WATCHLIST = "/root/my--project/watchlist.json"
ANDROID_DIR = "/root/storage/downloads"
ANDROID_WATCHLIST = f"{ANDROID_DIR}/watchlist.json"

print("Running copy_watchlist.py")
print("ARCH_WATCHLIST:", ARCH_WATCHLIST)
print("ANDROID_WATCHLIST:", ANDROID_WATCHLIST)

# --- Ensure Android Downloads exists ---
os.makedirs(ANDROID_DIR, exist_ok=True)
print("Verified Android Downloads directory exists.")

# --- Copy file ---
if os.path.exists(ARCH_WATCHLIST):
    shutil.copy(ARCH_WATCHLIST, ANDROID_WATCHLIST)
    print("Watchlist copied successfully.")
else:
    print("ERROR: watchlist.json not found in project folder.")

print("Done.")

