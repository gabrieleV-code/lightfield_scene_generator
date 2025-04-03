import os
from collections import Counter, defaultdict
import re

# Pattern to extract QP from filename and Luma_IntraMode from content
qp_pattern = re.compile(r'_(\d{2})\.vtmbmsstats$')
mode_pattern = re.compile(r'Luma_IntraMode=(\d+)')

def extract_qp(filename):
    """Extract QP value from filename."""
    match = filename.split('.')[-2].split('_')[1]
    return int(match) if match else None

def process_file(filepath):
    """Extract Luma_IntraMode occurrences from a .vtmbmsstats file."""
    mode_counts = Counter()
    with open(filepath, 'r') as file:
        for line in file:
            match = re.search(r"Luma_IntraMode=(\d+)", line)
            if match:
                mode = int(match.group(1))
                mode_counts[mode] += 1
    return mode_counts

def analyze_modes(directory):
    """Analyze all .vtmbmsstats files in a directory, compute mean usage per QP and overall,
    and print the top 10 modes by overall mean usage."""
    qp_mode_counts = defaultdict(Counter)
    total_counts = Counter()
    file_count_per_qp = defaultdict(int)

    # Process each file
    for filename in os.listdir(directory):
        if filename.endswith('.vtmbmsstats'):
            qp = extract_qp(filename)
            if qp:
                filepath = os.path.join(directory, filename)
                counts = process_file(filepath)
                qp_mode_counts[qp].update(counts)
                total_counts.update(counts)
                file_count_per_qp[qp] += 1

    # Compute mean usage per QP
    mean_usage_per_qp = {}
    print("QP modes usage:")
    for qp, counts in qp_mode_counts.items():
        total_blocks = sum(counts.values())
        mean_usage_per_qp[qp] = {mode: count / total_blocks for mode, count in counts.items()}
        print(f"QP {qp} mode usage:")
        top_10_modes = sorted(mean_usage_per_qp[qp].items(), key=lambda x: x[1], reverse=True)[:10]
        for mode, usage in top_10_modes:
            print(f"\tMode {mode}: {usage:.4f}")



    # Simple average across all QPs
    overall_mean_usage = {}
    modes = set().union(*[usage.keys() for usage in mean_usage_per_qp.values()])

        # Average usage across all QPs for each mode
    overall_mean_usage = {mode : sum(mean_usage_per_qp[qp].get(mode, 0) for qp in mean_usage_per_qp) / len(mean_usage_per_qp) for mode in modes}

    top_10_modes = sorted(overall_mean_usage.items(), key=lambda x: x[1], reverse=True)[:4]
    print("Simple average usage:")
    for mode, usage in top_10_modes:
        print(f"Mode {mode}: {usage:.4f}")

    # Assuming total_blocks_per_qp is a dictionary {QP: total_blocks}
    total_blocks_per_qp = {qp: sum(counts.values()) for qp, counts in qp_mode_counts.items()}

    # Compute weighted average
    overall_mean_usage_weighted = {}
    total_blocks_all = sum(total_blocks_per_qp.values())
    modes = set().union(*[usage.keys() for usage in mean_usage_per_qp.values()])
    print("Weighted average usage:")
    for mode in modes:
        weighted_sum = sum(mean_usage_per_qp[qp].get(mode, 0) * total_blocks_per_qp[qp] for qp in mean_usage_per_qp)
        overall_mean_usage_weighted[mode] = weighted_sum / total_blocks_all

    # Sort and print top 10 modes by overall mean usage
    top_10_modes = sorted(overall_mean_usage.items(), key=lambda x: x[1], reverse=True)[:4]
    print("Top 10 modes by overall mean usage:")
    for mode, usage in top_10_modes:
        print(f"Mode {mode}: {usage:.4f}")

    """ # Compute overall mean usage
    total_blocks_all = sum(total_counts.values())
    overall_mean_usage = {mode: count / total_blocks_all for mode, count in total_counts.items()}

    # Sort and print top 10 modes by overall mean usage
    top_10_modes = sorted(overall_mean_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top 10 modes by overall mean usage:")
    for mode, usage in top_10_modes:
        print(f"Mode {mode}: {usage:.4f}") """

    return mean_usage_per_qp, overall_mean_usage

# Example usage:
# directory_path = '/path/to/stats/files'
# mean_qp, mean_overall = analyze_modes(directory_path)
# print("Mean usage per QP:", mean_qp)

# Example usage:
directory_path = r'C:\Users\gabri\Lensltes_TESTSET_Finetuning_Pruned\decods_logs'
#directory_path = r'C:\Users\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs'

mean_qp, mean_overall = analyze_modes(directory_path)
#print("Mean usage per QP (top 10 modes):", mean_qp)
#print("Overall mean usage (top 10 modes):", mean_overall)
