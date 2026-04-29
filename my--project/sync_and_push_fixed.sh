#!/usr/bin/env bash
set -e

cd ~/my--project || exit 1

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv shell 3.14.0

python imfixed.py
python graphfixed.py

git add .
git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M:%S')" || true
git push	

