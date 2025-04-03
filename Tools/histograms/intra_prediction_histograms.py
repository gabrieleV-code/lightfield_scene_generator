from collections import Counter
import re
import matplotlib.pyplot as plt
import glob


# File pattern for multiple QP values
file_pattern = r"C:\Users\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs\Danger-de-Mort_9920x6912.yuv_*.vtmbmsstats"

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

# Sort QP values for consistent plotting
sorted_qps = sorted(qp_luma_modes.keys())

# Determine the global set of modes for consistent x-axis
all_modes = sorted(set().union(*[counter.keys() for counter in qp_luma_modes.values()]))

# Create subplots
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Luma Intra Modes per QP (Top 10 Highlighted)", fontsize=16)

for ax, qp in zip(axs.flatten(), sorted_qps):
    mode_counter = qp_luma_modes[qp]
    
    # Get frequencies for all modes (fill missing modes with 0)
    frequencies = [mode_counter.get(mode, 0) for mode in all_modes]
    
    # Identify top 10 modes
    top_modes = set([mode for mode, _ in mode_counter.most_common(10)])
    
    # Colors: Highlight top 10 modes, gray out the rest
    colors = ['skyblue' if mode in top_modes else 'lightgray' for mode in all_modes]
    
    # Plot all bars
    bars = ax.bar(all_modes, frequencies, color=colors, alpha=0.9)
    ax.set_title(f"QP {qp}", fontsize=14)
    ax.set_xlabel("Luma Intra Mode")
    ax.set_ylabel("Frequency")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Show x-ticks only for top 10 modes
    x_labels = [str(mode) if mode in top_modes else "" for mode in all_modes]
    ax.set_xticks(all_modes)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    
    # Add frequency labels for top 10 modes
    for bar, mode in zip(bars, all_modes):
        if mode in top_modes and bar.get_height() > 0:
            height = bar.get_height()
            ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

# Hide any unused subplots if fewer than 4 QP files
for i in range(len(sorted_qps), 4):
    fig.delaxes(axs.flatten()[i])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
