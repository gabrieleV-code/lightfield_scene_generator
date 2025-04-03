import os
from collections import Counter, defaultdict
import re

# Patterns to extract QP and Luma_IntraMode from content
qp_pattern = re.compile(r'_(\d{2})\.vtmbmsstats$')
mode_pattern = re.compile(r'Luma_IntraMode=(\d+)')

def extract_qp(filename):
    """Extract QP value from filename."""
    match = re.search(r"_(\d+)\.vtmbmsstats", filename)
    return int(match.group(1)) if match else None

def process_file(filepath):
    """Extract Luma_IntraMode occurrences from a .vtmbmsstats file."""
    mode_counts = Counter()
    with open(filepath, 'r') as file:
        for line in file:
            match = mode_pattern.search(line)
            if match:
                mode = int(match.group(1))
                mode_counts[mode] += 1
    return mode_counts

def print_mode_usage_means(directory):
    """Process all .vtmbmsstats files in the directory and print mode usage means overall and per QP."""
    total_counts = Counter()
    total_blocks = 0
    qp_mode_counts = defaultdict(Counter)
    qp_blocks = defaultdict(int)

    # Process each file
    for filename in os.listdir(directory):
        if filename.endswith('.vtmbmsstats'):
            qp = extract_qp(filename)
            filepath = os.path.join(directory, filename)
            counts = process_file(filepath)

            # Overall counts
            total_counts.update(counts)
            total_blocks += sum(counts.values())

            # Per QP counts
            if qp is not None:
                qp_mode_counts[qp].update(counts)
                qp_blocks[qp] += sum(counts.values())

    # Compute and sort overall mean usage
    overall_mean_usage = {mode: count / total_blocks for mode, count in total_counts.items()}
    sorted_overall = sorted(overall_mean_usage.items(), key=lambda x: x[1], reverse=True)

    # Print overall usage means
    print("Overall mode usage means (sorted by usage):")
    for mode, usage in sorted_overall[0:4]:
        print(f"Mode {mode}: {usage:.4f}")

    # Compute and print mean usage per QP
    print("\nMode usage means per QP (sorted by usage within each QP):")
    for qp, counts in sorted(qp_mode_counts.items()):
        print(f"\nQP {qp}:")
        total_qp_blocks = qp_blocks[qp]
        qp_mean_usage = {mode: count / total_qp_blocks for mode, count in counts.items()}
        sorted_qp = sorted(qp_mean_usage.items(), key=lambda x: x[1], reverse=True)
        for mode, usage in sorted_qp[0:4]:
            print(f"Mode {mode}: {usage:.4f}")

# Example usage:
# directory_path = '/path/to/stats/files'
# print_mode_usage_means(directory_path)

# Example usage:
directory_path = r'C:\Users\gabri\Ankylosaurus_9952x6912_Decodings\decods_logs'
print_mode_usage_means(directory_path)
