import os
import shutil
import matplotlib.pyplot as plt

# --- Paths ---
ARCH_GRAPH = "/root/my--project/test_graph.png"
ANDROID_DIR = "/root/storage/downloads/graphs"
ANDROID_GRAPH = f"{ANDROID_DIR}/test_graph.png"

# --- Debug prints ---
print("Running test_copy_graphs.py")
print("ARCH_GRAPH:", ARCH_GRAPH)
print("ANDROID_GRAPH:", ANDROID_GRAPH)

# --- Ensure Android folder exists ---
os.makedirs(ANDROID_DIR, exist_ok=True)
print("Verified Android directory exists.")

# --- Create a simple test graph ---
plt.figure(figsize=(6,4))
plt.plot([1,2,3,4], [10,20,15,30], marker="o")
plt.title("Test Graph Copy")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.savefig(ARCH_GRAPH)
plt.close()

print("Graph created at:", ARCH_GRAPH)

# --- Copy to Android storage ---
shutil.copy(ARCH_GRAPH, ANDROID_GRAPH)
print("Graph copied to:", ANDROID_GRAPH)

# --- Final confirmation ---
print("\nSUCCESS: Test graph copied to Android storage.")
