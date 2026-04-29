#!/bin/bash

# -----------------------------
# CONFIG
# -----------------------------
PROJECT="/root/my--project"
VENV="/root/pyenv/bin/activate"
COPY_SCRIPT="$PROJECT/copy_graphs.sh"

cd "$PROJECT" || exit 1

# -----------------------------
# ACTIVATE PYTHON ENV
# -----------------------------
if [ -f "$VENV" ]; then
    source "$VENV"
    echo "[OK] Virtual environment activated"
else
    echo "[ERROR] Virtual environment not found at $VENV"
    exit 1
fi

# -----------------------------
# RUN IMPORT SCRIPT
# -----------------------------
echo "[INFO] Running im.py..."
python3 "$PROJECT/im.py"
if [ $? -ne 0 ]; then
    echo "[ERROR] im.py failed"
    exit 1
fi

# -----------------------------
# RUN GRAPH GENERATION
# -----------------------------
echo "[INFO] Running graph.py..."
python3 "$PROJECT/graph.py"
if [ $? -ne 0 ]; then
    echo "[ERROR] graph.py failed"
    exit 1
fi

# -----------------------------
# RUN LOG GENERATION
# -----------------------------
echo "[INFO] Running log.py..."
python3 "$PROJECT/log.py"
if [ $? -ne 0 ]; then
    echo "[ERROR] log.py failed"
    exit 1
fi

# -----------------------------
# GIT COMMIT + PUSH
# -----------------------------
echo "[INFO] Git add/commit/push..."
git add .
git commit -m "Auto pipeline update"
git push
echo "[OK] Git push complete"

# -----------------------------
# COPY GRAPHS + LOGS TO ANDROID
# -----------------------------
if [ -f "$COPY_SCRIPT" ]; then
    echo "[INFO] Copying graphs + logs to Android..."
    bash "$COPY_SCRIPT"
else
    echo "[ERROR] copy_graphs.sh not found"
fi

echo "[DONE] Full pipeline completed successfully."
