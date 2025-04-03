import os
from collections import Counter, defaultdict
import re
import math

def extract_qp(filename):
    """Extract QP value from filename."""
    match = filename.split('.')[-2].split('_')[1]
    return int(match) if match else None

def process_file(filepath):
    """Extract Luma_IntraMode occurrences from a .vtmbmsstats file, weighted by block area."""
    mode_counts = Counter()
    with open(filepath, 'r') as file:
        for line in file:
            mode_match = re.search(r"Luma_IntraMode=(\d+)", line)
            block_size_match = re.search(r"\[(\d+)x(\d+)\]", line)
            
            if mode_match and block_size_match:
                mode = int(mode_match.group(1))
                width, height = map(int, block_size_match.groups())
                weight = width * height  # Compute block area
                mode_counts[mode] += weight  # Weighting by area
    return mode_counts

def analyze_modes(directory, output_file):
    """Analyze all .vtmbmsstats files in a directory, compute mean weighted usage and standard deviation per QP and overall."""
    qp_mode_counts = defaultdict(Counter)
    total_counts = Counter()
    file_count_per_qp = defaultdict(int)

    # Process each file
    for filename in os.listdir(directory):
        if filename.endswith('.vtmbmsstats') and "Ankylosaurus" in filename:
            qp = extract_qp(filename)
            if qp:
                filepath = os.path.join(directory, filename)
                counts = process_file(filepath)
                qp_mode_counts[qp].update(counts)
                total_counts.update(counts)
                file_count_per_qp[qp] += 1

    # Compute mean weighted usage per QP
    mean_usage_per_qp = {}
    std_dev_per_qp = {}
    with open(output_file, 'w') as out:
        out.write("QP modes weighted usage:\n")
        for qp, counts in qp_mode_counts.items():
            total_weight = sum(counts.values())
            mean_usage_per_qp[qp] = {mode: count / total_weight for mode, count in counts.items()}
            
            # Compute standard deviation per QP
            std_dev_per_qp[qp] = {}
            for mode in mean_usage_per_qp[qp]:
                mean = mean_usage_per_qp[qp][mode]
                variance = sum((count / total_weight - mean) ** 2 for count in qp_mode_counts[qp].values()) / len(qp_mode_counts[qp])
                std_dev_per_qp[qp][mode] = math.sqrt(variance)
            
            out.write(f"QP {qp} mode weighted usage:\n")
            top_10_modes = sorted(mean_usage_per_qp[qp].items(), key=lambda x: x[1], reverse=True)[:10]
            for mode, usage in top_10_modes:
                out.write(f"\tMode {mode}: Mean={usage:.4f}, StdDev={std_dev_per_qp[qp][mode]:.4f}\n")

        # Compute mean and standard deviation across QPs
        modes = set().union(*[usage.keys() for usage in mean_usage_per_qp.values()])
        overall_mean_usage = {mode: sum(mean_usage_per_qp[qp].get(mode, 0) for qp in mean_usage_per_qp) / len(mean_usage_per_qp) for mode in modes}
        
        std_dev_usage = {}
        for mode in modes:
            mean = overall_mean_usage[mode]
            variance = sum((mean_usage_per_qp[qp].get(mode, 0) - mean) ** 2 for qp in mean_usage_per_qp) / len(mean_usage_per_qp)
            std_dev_usage[mode] = math.sqrt(variance)
        
        out.write("Overall mean weighted usage and standard deviation:\n")
        top_10_modes = sorted(overall_mean_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        for mode, usage in top_10_modes:
            out.write(f"Mode {mode}: Mean={usage:.4f}, StdDev={std_dev_usage[mode]:.4f}\n")
    
    return mean_usage_per_qp, std_dev_per_qp, overall_mean_usage, std_dev_usage

# Example usage:
directory_path = r'C:\Users\gabri\Lensltes_TESTSET_Finetuning_Pruned\decods_logs'
output_file_path =os.path.join(os.path.join(directory_path,".."), 'mode_analysis_results_Ankylosaurus.txt')
mean_qp, std_dev_qp, mean_overall, std_dev_overall = analyze_modes(directory_path, output_file_path)
