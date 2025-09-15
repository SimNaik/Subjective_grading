import csv

input_mmd = "merged_output.mmd"   # Change this if your file is named differently
output_csv = "merged_output.csv"

rows = []
header_found = False
with open(input_mmd, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Skip separator lines (those with only dashes and pipes)
        if set(line.replace('|', '').replace(':', '').replace('-', '')) == set():
            continue
        if line.startswith('|'):
            # Remove leading/trailing pipes and split
            parts = [cell.strip() for cell in line.strip('|').split('|')]
            if not header_found:
                header_found = True
                rows.append(parts[:4])  # keep header
                continue
            # Keep only the first 4 columns
            rows.append(parts[:4])

# Write to CSV
with open(output_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

# Print number of data rows (excluding header)
print(f"Converted {input_mmd} to {output_csv} (first 4 columns only)")
print(f"Number of data rows (excluding header): {len(rows) - 1}") 