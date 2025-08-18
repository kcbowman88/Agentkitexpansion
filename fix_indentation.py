import re

def fix_indentation(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    fixed_lines = []
    for line in lines:
        # Replace leading tabs with 4 spaces
        new_line = line.replace('\t', '    ')
        fixed_lines.append(new_line)

    with open(filepath, 'w') as f:
        f.writelines(fixed_lines)

if __name__ == "__main__":
    fix_indentation('objection_handler.py')