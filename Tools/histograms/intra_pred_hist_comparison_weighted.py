import glob
from collections import Counter
import re
import matplotlib.pyplot as plt
import numpy as np

group1_name = 'Friends-1_9952x6912'
group2_name = group1_name

group1_name_f = group1_name.split('_')[0]
group2_name_f = group2_name.split('_')[0]

# File patterns for the two groups (adjust paths accordingly)
group1_pattern = fr"C:\Users\gabri\Lensltes_TESTSET_Finetuning_Pruned\decods_logs\{group2_name}.yuv_*.vtmbmsstats"
group2_pattern = fr"C:\Users\gabri\Lenslets_NN_Finetuned4_PRUNED_001\decods_logs\{group1_name}.yuv_*.vtmbmsstats"

""" def process_group(file_pattern):
    qp_luma_modes = {}
    for file_path in glob.glob(file_pattern):
        qp_value = re.search(r"_(\d+)\.vtmbmsstats", file_path)
        if qp_value:
            qp = int(qp_value.group(1))
        else:
            continue
        mode_counter = Counter()
        
        with open(file_path, "r") as file:
            for line in file:
                mode_match = re.search(r"Luma_IntraMode=(\d+)", line)
                block_size_match = re.search(r"\[(\d+)x(\d+)\]", line)
                
                if mode_match and block_size_match:
                    mode = int(mode_match.group(1))
                    width, height = map(int, block_size_match.groups())
                    weight = width * height  # Compute block area
                    
                    mode_counter[mode] += weight  # Weighting by area
        
        qp_luma_modes[qp] = mode_counter
    return qp_luma_modes

# Process both groups
group1_modes = process_group(group1_pattern)
group2_modes = process_group(group2_pattern)

# Common QPs and modes
common_qps = sorted(set(group1_modes.keys()) & set(group2_modes.keys()))
total_mode_counts = Counter()
for mode_counts in list(group1_modes.values()) + list(group2_modes.values()):
    total_mode_counts.update(mode_counts)

top_modes = [mode for mode, _ in total_mode_counts.most_common(4)]

# Calculate percentages with weighted counts
def calculate_percentages(qp_luma_modes):
    total_weights = np.array([sum(qp_luma_modes[qp].get(mode, 0) for mode in top_modes) for qp in common_qps])
    mode_frequencies = {mode: [qp_luma_modes[qp].get(mode, 0) for qp in common_qps] for mode in top_modes}
    return {mode: np.divide(mode_frequencies[mode], total_weights, out=np.zeros_like(mode_frequencies[mode], dtype=float), where=total_weights!=0) * 100 for mode in top_modes}

percentages_group1 = calculate_percentages(group1_modes)
percentages_group2 = calculate_percentages(group2_modes)

# Plot stacked bar chart
highlight_colors = ["#08306b", "#4292c6", "#9ecae1", "#ff9900"]
mode_labels = {0: "DC", 1: "Planar", 2: "Angulars", 3: "NN Mode"}
bar_width = 0.25
x_indexes = np.arange(len(common_qps))

plt.figure(figsize=(9, 5))
bottom1 = np.zeros(len(common_qps))
bottom2 = np.zeros(len(common_qps))

for mode in top_modes:
    plt.bar(x_indexes - 0.6 * bar_width, percentages_group1[mode], width=bar_width, bottom=bottom1, 
            label=mode_labels.get(mode, f"Mode {mode}"), color=highlight_colors[top_modes.index(mode)])
    plt.bar(x_indexes + 0.6 * bar_width, percentages_group2[mode], width=bar_width, bottom=bottom2, 
            color=highlight_colors[top_modes.index(mode)], alpha=0.9)
    bottom1 += percentages_group1[mode]
    bottom2 += percentages_group2[mode]

plt.xlabel("QP Value")
plt.ylabel("% of Weighted Selection")
plt.title("Weighted Luma Intra Mode Distribution Across QPs")
plt.xticks(x_indexes, common_qps)
plt.legend(loc='upper right', ncol=2)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show(block=True)
 """


def process_group(file_pattern):
    qp_luma_modes = {}
    for file_path in glob.glob(file_pattern):
        qp_value = re.search(r"_(\d+)\.vtmbmsstats", file_path)
        if qp_value:
            qp = int(qp_value.group(1))
        else:
            continue
        mode_counter = Counter()
        
        with open(file_path, "r") as file:
            for line in file:
                mode_match = re.search(r"Luma_IntraMode=(\d+)", line)
                block_size_match = re.search(r"\[(\d+)x(\d+)\]", line)
                
                if mode_match and block_size_match:
                    mode = int(mode_match.group(1))
                    width, height = map(int, block_size_match.groups())
                    weight = width * height  # Compute block area
                    
                    mode_counter[mode] += weight  # Weighting by area
        
        qp_luma_modes[qp] = mode_counter
    return qp_luma_modes

# Process both groups
group1_modes = process_group(group1_pattern)
group2_modes = process_group(group2_pattern)

# Common QPs and modes
common_qps = sorted(set(group1_modes.keys()) & set(group2_modes.keys()))
total_mode_counts = Counter()
for mode_counts in list(group1_modes.values()) + list(group2_modes.values()):
    total_mode_counts.update(mode_counts)

top_modes = [mode for mode, _ in total_mode_counts.most_common(4)]

# Calculate percentages with weighted counts
def calculate_percentages(qp_luma_modes):
    total_weights = np.array([sum(qp_luma_modes[qp].get(mode, 0) for mode in top_modes) for qp in common_qps])
    mode_frequencies = {mode: [qp_luma_modes[qp].get(mode, 0) for qp in common_qps] for mode in top_modes}
    return {mode: np.divide(mode_frequencies[mode], total_weights, out=np.zeros_like(mode_frequencies[mode], dtype=float), where=total_weights!=0) * 100 for mode in top_modes}

percentages_group1 = calculate_percentages(group1_modes)
percentages_group2 = calculate_percentages(group2_modes)

# Plot stacked bar chart
highlight_colors = ["#08306b", "#4292c6", "#9ecae1", "#ff9900"]
mode_labels = {0: "DC", 1: "Planar", 2: "Angulars", 3: "NN Mode"}
def get_color(mode):
    if mode == 34: c = '#f88379'
    else: c = (highlight_colors[top_modes.index(mode)] if mode in top_modes else "#cccccc")
    return c
bar_width = 0.25
x_indexes = np.arange(len(common_qps))

def plot_group_stacked(x_pos, percentages_group, show_label=False):
    bottom = np.zeros(len(common_qps))
    for mode in top_modes:
        plt.bar(x_pos, percentages_group[mode], width=bar_width, bottom=bottom, 
                label=mode_labels.get(mode, f"Mode {mode}") if show_label else None, 
                color=get_color(mode))
        bottom += percentages_group[mode]

plt.figure(figsize=(9, 5))
plot_group_stacked(x_indexes - 0.6 * bar_width, percentages_group1, show_label=True)
plot_group_stacked(x_indexes + 0.6 * bar_width, percentages_group2)

# Add Baseline/Proposed labels above each column group
for i, qp in enumerate(common_qps):
    plt.text(x_indexes[i] - 0.6 * bar_width, 75, "Reference", ha='center', fontsize=15, color='black', rotation=80)
    plt.text(x_indexes[i] + 0.6 * bar_width, 75, "Proposed", ha='center', fontsize=15, color='black', rotation=80)

plt.xlabel("QP Value")
plt.ylabel("% of Weighted Selection")
plt.title(f"Luma Intra Mode Distribution Across QPs for {group1_name}")
plt.xticks(x_indexes, common_qps)
plt.legend(loc='upper right', ncol=2)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

import os
plt.savefig(os.path.join(r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\Tesi",group1_name+"_vettoriale.pdf"), format="pdf")

plt.show()