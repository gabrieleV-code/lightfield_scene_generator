from collections import Counter
import re
import matplotlib.pyplot as plt
import glob
import numpy as np

# File pattern for multiple QP values
file_pattern = r"C:\Users\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs\Ankylosaurus_9952x6912.yuv_*.vtmbmsstats"


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

# Sort QP values
sorted_qps = sorted(qp_luma_modes.keys())
all_modes = sorted(set().union(*[counter.keys() for counter in qp_luma_modes.values()]))

# Identify the 4 most important modes (highest frequency overall)
total_mode_counts = Counter()
for mode_counts in qp_luma_modes.values():
    total_mode_counts.update(mode_counts)

top_modes = [mode for mode, _ in total_mode_counts.most_common(4)]
all_modes = top_modes
# Prepare data for stacked bar chart
mode_frequencies = {mode: [qp_luma_modes[qp].get(mode, 0) for qp in sorted_qps] for mode in all_modes}
mode_labels = {0: "DC", 1: "Planar", 2: "Angulars", 3: "NN Mode"}  # Example labels (adjust as needed)

# Convert counts to percentages
total_counts = np.array([sum(qp_luma_modes[qp].values()) for qp in sorted_qps])
mode_percentages = {mode: np.array(mode_frequencies[mode]) / total_counts * 100 for mode in all_modes}

# Define colors (highlight top 4 modes, others in gray)
highlight_colors = ["#08306b", "#4292c6", "#9ecae1", "#ff9900"]
def get_color(mode):
    return highlight_colors[top_modes.index(mode)] if mode in top_modes else "#cccccc"

# Plot stacked bar chart
plt.figure(figsize=(12, 6))
x_indexes = np.arange(len(sorted_qps))
bottom = np.zeros(len(sorted_qps))

for mode in all_modes:
    plt.bar(x_indexes, mode_percentages[mode], label= mode_labels.get(mode, f"Mode {mode}") if mode in top_modes else None, 
            bottom=bottom, color=get_color(mode))
    bottom += mode_percentages[mode]

plt.xlabel("QP Value")
plt.ylabel("% of Selection")
plt.title("Luma Intra Mode Distribution Across QPs (Stacked)")
plt.xticks(x_indexes, sorted_qps)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show(block=True)  # Keep the plot open