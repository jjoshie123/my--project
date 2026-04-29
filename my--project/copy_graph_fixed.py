#!/data/data/com.termux/files/usr/bin/python

import os
import shutil
import subprocess

SRC = "/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/archlinux/root/graphs"
DEST = os.path.expanduser("~/storage/downloads/graphs")

os.makedirs(DEST, exist_ok=True)

if os.path.exists(SRC):
    for f in os.listdir(SRC):
        if f.endswith(".png"):
            shutil.copy2(os.path.join(SRC, f), os.path.join(DEST, f))
else:
    print("Source folder missing:", SRC)

try:
    subprocess.run([
        "termux-notification",
        "--title", "Graphs Copied",
        "--content", "Graphs moved to Downloads/graphs"
    ])
except:
    pass
