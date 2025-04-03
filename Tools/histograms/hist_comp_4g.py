
from collections import Counter
import re
import matplotlib.pyplot as plt
import glob
import numpy as np

# File patterns for the four groups
group1_pattern = r"C:\Users\\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs\Ankylosaurus_9952x6912.yuv_*.vtmbmsstats"  # Baseline 1
group2_pattern = r"C:\Users\gabri\Lenslets_NO_NN\decods_logs\Ankylosaurus_9952x6912.yuv_*.vtmbmsstats"  # Proposed 1
group3_pattern = r"C:\Users\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs\Danger-de-Mort_9920x6912.yuv_*.vtmbmsstats"  # Baseline 2
group4_pattern = r"C:\Users\gabri\Lenslets_NO_NN\decods_logs\Danger-de-Mort_9920x6912.yuv_*.vtmbmsstats"  # Proposed 2

def process_group(file_pattern):
    qp_luma_modes = {}
    group_name = None
    for file_path in glob.glob(file_pattern):
        if group_name is None:
            group_name_match = re.search(r"\\\\([^_]+)_", file_path)
            group_name = group_name_match.group(1) if group_name_match else "Unknown"

        qp_value = re.search(r"_(\\d+)\\.vtmbmsstats", file_path)
        if qp_value:
            qp = int(qp_value.group(1))
        else:
            continue
        luma_mode_counter = Counter()
        with open(file_path, "r") as file:
            for line in file:
                match = re.search(r"Luma_IntraMode=(\\d+)", line)
                if match:
                    mode = int(match.group(1))
                    luma_mode_counter[mode] += 1
        qp_luma_modes[qp] = luma_mode_counter
    return group_name, qp_luma_modes

# Process all four groups
group1_name, group1_modes = process_group(group1_pattern)
group2_name, group2_modes = process_group(group2_pattern)
group3_name, group3_modes = process_group(group3_pattern)
group4_name, group4_modes = process_group(group4_pattern)

# Common QPs and modes
common_qps = sorted(set(group1_modes.keys()) & set(group2_modes.keys()) & set(group3_modes.keys()) & set(group4_modes.keys()))
all_modes = sorted(set().union(*[group1_modes[qp].keys() for qp in common_qps],
                               *[group2_modes[qp].keys() for qp in common_qps],
                               *[group3_modes[qp].keys() for qp in common_qps],
                               *[group4_modes[qp].keys() for qp in common_qps]))

# Top 4 modes overall
total_mode_counts = Counter()
for mode_counts in list(group1_modes.values()) + list(group2_modes.values()) + list(group3_modes.values()) + list(group4_modes.values()):
    total_mode_counts.update(mode_counts)

top_modes = [mode for mode, _ in total_mode_counts.most_common(4)]
all_modes = top_modes

# Prepare data for plotting (element-wise division per QP with 100% for top modes)
def calculate_percentages(qp_luma_modes):
    mode_frequencies = {mode: np.array([qp_luma_modes[qp].get(mode, 0) for qp in common_qps]) for mode in all_modes}
    top_mode_totals = np.sum([mode_frequencies[mode] for mode in all_modes], axis=0)
    return {mode: np.divide(mode_frequencies[mode], top_mode_totals, out=np.zeros_like(mode_frequencies[mode], dtype=float), where=top_mode_totals != 0) * 100 for mode in all_modes}

percentages_group1 = calculate_percentages(group1_modes)
percentages_group2 = calculate_percentages(group2_modes)
percentages_group3 = calculate_percentages(group3_modes)
percentages_group4 = calculate_percentages(group4_modes)

# Visualization with stacked bars per group per QP
highlight_colors = ["#08306b", "#4292c6", "#9ecae1", "#ff9900"]
mode_labels = {0: "DC", 1: "Planar", 2: "Angulars", 3: "NN Mode"}

def get_color(mode):
    return highlight_colors[top_modes.index(mode)] if mode in top_modes else "#cccccc"

bar_width = 0.18
x_indexes = np.arange(len(common_qps))

def plot_group_stacked(x_pos, percentages_group, group_name, alpha):
    bottom = np.zeros(len(common_qps))
    for mode in all_modes:
        plt.bar(x_pos, percentages_group[mode], width=bar_width, bottom=bottom,
                label=f"{group_name} - {mode_labels.get(mode, f'Mode {mode}')}" if mode == all_modes[0] else None,
                color=get_color(mode), alpha=alpha)
        bottom += percentages_group[mode]

plt.figure(figsize=(16, 8))
plot_group_stacked(x_indexes - 1.5 * bar_width, percentages_group1, f"{group1_name} (Baseline 1)", alpha=0.7)
plot_group_stacked(x_indexes - 0.5 * bar_width, percentages_group2, f"{group2_name} (Proposed 1)", alpha=0.5)
plot_group_stacked(x_indexes + 0.5 * bar_width, percentages_group3, f"{group3_name} (Baseline 2)", alpha=0.7)
plot_group_stacked(x_indexes + 1.5 * bar_width, percentages_group4, f"{group4_name} (Proposed 2)", alpha=0.5)

# Add Baseline/Proposed labels above each column group
for i, qp in enumerate(common_qps):
    plt.text(x_indexes[i] - bar_width, 105, "Baseline", ha='center', fontsize=10, color='black', rotation=45)
    plt.text(x_indexes[i] + bar_width, 105, "Proposed", ha='center', fontsize=10, color='black', rotation=45)

plt.xlabel("QP Value")
plt.ylabel("% of Top Mode Selection per QP")
plt.title("Comparison of Luma Intra Mode Distribution Across QPs (Stacked Bars per Group per QP)")
plt.xticks(x_indexes, common_qps)
plt.legend(loc='upper right', ncol=2)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show(block=True)
