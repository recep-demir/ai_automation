import os
import sys

output_file = "filtered_results.txt"
if len(sys.argv) != 3:
    print("Usage: python task_3.py <file_name> <searched_keyword>")
    sys.exit(1)
file_name = sys.argv[1]
searched_keyword = sys.argv[2].upper()


if not os.path.exists(file_name):
    print(f"Error: The file '{file_name}' was not found!")
    sys.exit(1)

try:
    with open(file_name, 'r', encoding='utf-8') as source_file:
        with open(output_file, "w", encoding="utf-8") as target_file:
            for line_number, line in enumerate(source_file, 1):
                 line = line.strip()
                 if searched_keyword in line.upper():
                     target_file.write(f"Line{line_number} {line}\n")
    print(f"Success! Results saved to {output_file}")


except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit()

