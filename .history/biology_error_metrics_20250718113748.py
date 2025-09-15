import os

md_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Biology/Biology_final.md"
metrics_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Biology/metrics.txt"

error_types = [
    "Spelling",
    "Punctuation",
    "Wording",
    "Numerical Difference",
    "NO ERRORS",
    "Content Mix-up",
    "Missing Content",
    "Extra Content",
    "Capitalization",
    "Omission"
]

try:
    with open(md_path, 'r') as f:
        lines = f.readlines()

    # Parse markdown table
    table = []
    for line in lines:
        line = line.strip()
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line[1:-1].split('|')]
            table.append(cells)

    if len(table) < 2:
        raise Exception("Table too short or missing header.")

    header = table[0]
    try:
        error_idx = [h.lower().replace(' ', '') for h in header].index('typeoferror')
    except ValueError:
        raise Exception("No 'type of error' column found in header.")

    data_rows = table[2:]  # skip header and separator
    total_rows = len(data_rows)
    error_counts = {etype: 0 for etype in error_types}

    for row in data_rows:
        if error_idx < len(row):
            val = row[error_idx].strip()
            for etype in error_types:
                if etype.lower() in val.lower():
                    error_counts[etype] += 1

    # Write metrics to file in requested format
    with open(metrics_path, 'w') as f:
        f.write("Discrepancy Type\n\n")
        f.write("Count\n\n")
        f.write("Percentage of Total Entries (Rounded)\n\n")
        for etype in error_types:
            count = error_counts[etype]
            percent = (count / total_rows * 100) if total_rows else 0
            percent_str = f"{percent:.2f}%"
            f.write(f"{etype}\n\n{count}\n\n{percent_str}\n\n")

except Exception as e:
    print(f"Error: {e}") 