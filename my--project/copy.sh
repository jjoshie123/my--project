#!/bin/bash

# SOURCE DIRECTORIES (inside Arch)
GRAPHS_SRC="/root/my--project/graphs"
LOGS_SRC="/root/my--project/logs"

# DESTINATION DIRECTORIES (Android storage)
GRAPHS_DEST="/root/storage/shared/Download/graphs"
LOGS_DEST="/root/storage/shared/Download/logs"

# Create destination directories if missing
mkdir -p "$GRAPHS_DEST"
mkdir -p "$LOGS_DEST"

echo "[INFO] Copying graphs..."
cp -r "$GRAPHS_SRC"/* "$GRAPHS_DEST"/ 2>/dev/null

echo "[INFO] Copying logs..."
cp -r "$LOGS_SRC"/* "$LOGS_DEST"/ 2>/dev/null

echo "[OK] All graphs and logs copied to Android Downloads."
echo "[DONE] Location:"
echo " - Graphs: /sdcard/Download/graphs/"
echo " - Logs:   /sdcard/Download/logs/"
