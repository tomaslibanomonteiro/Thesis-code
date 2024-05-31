import os
import glob

def count_non_empty_lines_in_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    non_empty_lines = [line for line in lines if line.strip() != '']
    return len(non_empty_lines)

def count_non_empty_lines_in_dir(directory):
    total_lines = 0
    for filepath in glob.glob(os.path.join(directory, '**', '*.py'), recursive=True):
        total_lines += count_non_empty_lines_in_file(filepath)
    return total_lines

root_directory = r"C:\Users\tomas\OneDrive - Universidade de Lisboa\Desktop\Tese\Thesis-code"
output_file = 'lines_of_code.txt'

with open(output_file, 'w') as f:
    for directory in glob.glob(os.path.join(root_directory, '*')):
        if os.path.isdir(directory):
            folder_name = os.path.basename(directory)
            f.write(f'Total non-empty lines in .py files in directory {folder_name} and its subdirectories: {count_non_empty_lines_in_dir(directory)}\n')