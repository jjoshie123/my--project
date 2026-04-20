copy_watchlist_arch() {
    LOG="/root/storage/downloads/pv-log.txt"
    SRC="/root/my--project/watchlist.json"
    DEST="/root/storage/downloads/watchlist.json"

    echo "[*] Arch copy: $SRC → $DEST" | tee -a "$LOG"

    # Auto-repair: ensure source exists
    if [ ! -f "$SRC" ]; then
        echo "[AUTO-REPAIR] watchlist.json missing. Creating default." | tee -a "$LOG"
        echo '{"tickers": [], "favorites": []}' > "$SRC"
    fi

    # Ensure destination directory exists
    mkdir -p /root/storage/downloads

    # Copy file
    if cp "$SRC" "$DEST" 2>>"$LOG"; then
        echo "[OK] watchlist.json copied to Android Downloads" | tee -a "$LOG"
    else
        echo "[ERROR] Failed to copy watchlist.json" | tee -a "$LOG"
    fi
}
