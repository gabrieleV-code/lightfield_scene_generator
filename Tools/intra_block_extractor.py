from collections import Counter
import re
import matplotlib.pyplot as plt

# File path
file_path = r"C:\Users\gabri\Ankylosaurus_9952x6912.yuv_37.vtmbmsstats"

# Dictionary to store Luma Intra Mode counts
luma_mode_counter = Counter()

# Read and process the file
with open(file_path, "r") as file:
    for line in file:
        match = re.search(r"Luma_IntraMode=(\d+)", line)
        if match:
            mode = int(match.group(1))
            luma_mode_counter[mode] += 1

# Print the top Luma Intra Modes
print("Luma Intra Mode Frequency:")
for mode, count in luma_mode_counter.most_common():
    print(f"Mode {mode}: {count} occurrences")

# Plot histogram
plt.figure(figsize=(10, 5))
plt.bar(luma_mode_counter.keys(), luma_mode_counter.values(), color='blue')
plt.xlabel("Luma Intra Mode")
plt.ylabel("Frequency")
plt.title("Histogram of Luma Intra Modes")
plt.xticks(sorted(luma_mode_counter.keys()))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

from collections import Counter
import re
import matplotlib.pyplot as plt
import glob

# File pattern for multiple QP values
file_pattern = r"C:\Users\gabri\Ankylosaurus_9952x6912.yuv_*.vtmbmsstats"

# Dictionary to store Luma Intra Mode counts per QP
qp_luma_modes = {}

# Process each file matching the pattern
for file_path in glob.glob(file_pattern):
    qp_value = re.search(r"_(\d+)\.vtmbmsstats", file_path)
    if qp_value:
        qp = int(qp_value.group(1))
    else:
        continue

    luma_mode_counter = Counter()
    
    # Read and process the file
    with open(file_path, "r") as file:
        for line in file:
            match = re.search(r"Luma_IntraMode=(\d+)", line)
            if match:
                mode = int(match.group(1))
                luma_mode_counter[mode] += 1
    
    qp_luma_modes[qp] = luma_mode_counter

# Plot histograms for each QP value
plt.figure(figsize=(12, 6))
for qp, mode_counter in sorted(qp_luma_modes.items()):
    plt.bar(mode_counter.keys(), mode_counter.values(), alpha=0.7, label=f"QP {qp}")

plt.xlabel("Luma Intra Mode")
plt.ylabel("Frequency")
plt.title("Histogram of Luma Intra Modes for Different QP Values")
plt.xticks(sorted(set().union(*[counter.keys() for counter in qp_luma_modes.values()])))
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
