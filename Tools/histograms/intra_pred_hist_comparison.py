from collections import Counter
import re
import matplotlib.pyplot as plt
import glob
import numpy as np


#group1_name = 'Ankylosaurus_9952x6912'
group1_name = 'Friends-1_9952x6912'
group2_name = group1_name

group1_name_f = group1_name.split('_')[0]
group2_name_f = group2_name.split('_')[0]

# File patterns for the two groups
group1_pattern = fr"C:\Users\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs\{group2_name}.yuv_*.vtmbmsstats"
group2_pattern = fr"C:\Users\gabri\Lensltes_TESTSET_Finetuning_Pruned\decods_logs\{group1_name}.yuv_*.vtmbmsstats"

def process_group(file_pattern):
    qp_luma_modes = {}
    group_name = None
    for file_path in glob.glob(file_pattern):
        if group_name is None:
            group_name = file_path.split('\\')[-1].split('_')[0]
            #group_name = group_name_match.group(1) if group_name_match else "Unknown"

        qp_value = re.search(r"_(\d+)\.vtmbmsstats", file_path)
        if qp_value:
            qp = int(qp_value.group(1))
        else:
            continue
        luma_mode_counter = Counter()
        with open(file_path, "r") as file:
            for line in file:
                match = re.search(r"Luma_IntraMode=(\d+)", line)
                if match:
                    mode = int(match.group(1))
                    luma_mode_counter[mode] += 1
        qp_luma_modes[qp] = luma_mode_counter
    return group_name, qp_luma_modes

# Process all four groups
group1_name, group1_modes = process_group(group1_pattern)
group2_name, group2_modes = process_group(group2_pattern)

# Common QPs and modes
common_qps = sorted(set(group1_modes.keys()) & set(group2_modes.keys()))
all_modes = sorted(set().union(*[group1_modes[qp].keys() for qp in common_qps], *[group2_modes[qp].keys() for qp in common_qps]))

# Top 4 modes overall
total_mode_counts = Counter()
for mode_counts in list(group1_modes.values()) + list(group2_modes.values()):
    total_mode_counts.update(mode_counts)

top_modes = [mode for mode, _ in total_mode_counts.most_common(4)]
all_modes = top_modes

# Prepare data for plotting
def calculate_percentages(qp_luma_modes):
    total_counts = np.array([sum([qp_luma_modes[qp].get(mode, 0) for mode in all_modes]) for qp in common_qps])
    mode_frequencies = {mode: [qp_luma_modes[qp].get(mode, 0) for qp in common_qps] for mode in all_modes}
    #check= sum([mode_frequencies.get(mode, 0)[0] for mode in all_modes])
    return {mode: np.divide(mode_frequencies[mode], total_counts, out=np.zeros_like(mode_frequencies[mode], dtype=float), where=total_counts!=0) * 100 for mode in all_modes}
    #{mode: np.array(mode_frequencies[mode]) / total_counts * 100 for mode in all_modes}

percentages_group1 = calculate_percentages(group1_modes)
percentages_group2 = calculate_percentages(group2_modes)

# Visualization
highlight_colors = ["#08306b", "#4292c6", "#9ecae1", "#ff9900"]
mode_labels = {0: "DC", 1: "Planar", 2: "Angulars", 3: "NN Mode"}
def get_color(mode):
    if mode == 34: c = '#f88379'
    else: c = (highlight_colors[top_modes.index(mode)] if mode in top_modes else "#cccccc")
    return c

bar_width = 0.25
x_indexes = np.arange(len(common_qps))

def plot_group_stacked(x_pos, percentages_group, group_name, alpha,show_label = False):
    bottom = np.zeros(len(common_qps))
    for mode in all_modes:
        plt.bar(x_pos, percentages_group[mode], width=bar_width, bottom=bottom,
                label=f"{mode_labels.get(mode, f'Mode {mode}')}" if (show_label) else None,
                color=get_color(mode), alpha=alpha)
        bottom += percentages_group[mode]

plt.figure(figsize=(9, 5))

plot_group_stacked(x_indexes - 0.6 *bar_width, percentages_group1, f"{group1_name} (Reference 1)", alpha=1,show_label=True)
plot_group_stacked(x_indexes + 0.6 *bar_width, percentages_group2, f"{group2_name} (Proposed 1)", alpha=1)
#for i, mode in enumerate(all_modes[0:2]):
    #plt.bar(x_indexes - (0.1+bar_width/2), percentages_group1[mode], width=bar_width, label=f"Group 1 - {mode_labels.get(mode, f'Mode {mode}')}", color=get_color(mode), alpha=0.7)
    #plt.bar(x_indexes + (0.1+bar_width/2), percentages_group2[mode], width=bar_width, label=f"Group 2 - {mode_labels.get(mode, f'Mode {mode}')}", color=get_color(mode), alpha=0.4)

# Add Baseline/Proposed labels above each column group
for i, qp in enumerate(common_qps):
    plt.text(x_indexes[i] - 0.6 * bar_width, 75, "Reference", ha='center', fontsize=15, color='black', rotation=55)
    plt.text(x_indexes[i] + 0.6 * bar_width, 75, "Proposed", ha='center', fontsize=15, color='black', rotation=55)

plt.xlabel("QP Value")
plt.ylabel("% of Selection")
plt.title(f"Comparison of Luma Intra Mode Distribution Across QPs for {group1_name}")
plt.xticks(x_indexes, common_qps)
plt.legend(loc='upper right', ncol=2)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show(block=True)
