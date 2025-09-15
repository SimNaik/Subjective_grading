import os
import sys

def combine_mmd_files(directory, output_file='combined.mmd'):
    # Get all .mmd files in the directory
    mmd_files = [f for f in os.listdir(directory) if f.endswith('.mmd')]
    mmd_files.sort()  # Optional: sort files alphabetically

    if not mmd_files:
        print(f'No .mmd files found in {directory}')
        return

    combined_rows = []
    for idx, filename in enumerate(mmd_files):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if idx == 0:
                combined_rows.extend(lines)
            else:
                combined_rows.extend(lines[1:])  # Skip header row

    output_path = os.path.join(directory, output_file)
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.writelines(combined_rows)
    print(f'Combined {len(mmd_files)} files into {output_path}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python combine_mmd.py <directory> [output_file]')
        sys.exit(1)
    directory = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'combined.mmd'
    combine_mmd_files(directory, output_file) 