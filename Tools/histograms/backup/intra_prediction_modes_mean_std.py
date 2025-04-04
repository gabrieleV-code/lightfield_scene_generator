import os
from collections import Counter, defaultdict
import re
import math

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
    """Analyze all .vtmbmsstats files in a directory, compute mean usage and standard deviation per QP and overall."""
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
    std_dev_per_qp = {}
    print("QP modes usage:")
    for qp, counts in qp_mode_counts.items():
        total_blocks = sum(counts.values())
        mean_usage_per_qp[qp] = {mode: count / total_blocks for mode, count in counts.items()}
        
        # Compute standard deviation per QP
        std_dev_per_qp[qp] = {}
        for mode in mean_usage_per_qp[qp]:
            mean = mean_usage_per_qp[qp][mode]
            variance = sum((count / total_blocks - mean) ** 2 for count in qp_mode_counts[qp].values()) / len(qp_mode_counts[qp])
            std_dev_per_qp[qp][mode] = math.sqrt(variance)
        
        print(f"QP {qp} mode usage:")
        top_10_modes = sorted(mean_usage_per_qp[qp].items(), key=lambda x: x[1], reverse=True)[:10]
        for mode, usage in top_10_modes:
            print(f"\tMode {mode}: Mean={usage:.4f}, StdDev={std_dev_per_qp[qp][mode]:.4f}")

    # Compute mean and standard deviation across QPs
    modes = set().union(*[usage.keys() for usage in mean_usage_per_qp.values()])
    overall_mean_usage = {mode: sum(mean_usage_per_qp[qp].get(mode, 0) for qp in mean_usage_per_qp) / len(mean_usage_per_qp) for mode in modes}
    
    std_dev_usage = {}
    for mode in modes:
        mean = overall_mean_usage[mode]
        variance = sum((mean_usage_per_qp[qp].get(mode, 0) - mean) ** 2 for qp in mean_usage_per_qp) / len(mean_usage_per_qp)
        std_dev_usage[mode] = math.sqrt(variance)
    
    top_10_modes = sorted(overall_mean_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Overall mean usage and standard deviation:")
    for mode, usage in top_10_modes:
        print(f"Mode {mode}: Mean={usage:.4f}, StdDev={std_dev_usage[mode]:.4f}")

    return mean_usage_per_qp, std_dev_per_qp, overall_mean_usage, std_dev_usage

# Example usage:
directory_path = r'C:\Users\gabri\Lensltes_TESTSET_Finetuning_Pruned\decods_logs'
#directory_path = r'C:\Users\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs'
mean_qp, std_dev_qp, mean_overall, std_dev_overall = analyze_modes(directory_path)
