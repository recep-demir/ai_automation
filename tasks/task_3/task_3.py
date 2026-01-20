import os   # Import the OS module to handle file path and existence checks
import sys  # Import the Sys module to access command-line arguments

# Define the name of the output file as a constant
output_file = "filtered_results.txt"

# Check if the required number of command-line arguments (file_name and keyword) are provided
# sys.argv[0] is the script name, so we expect 3 items in total
if len(sys.argv) != 3:
    print("Usage: python task_3.py <file_name> <searched_keyword>")
    sys.exit(1) # Exit the script with an error code

# Assign command-line arguments to descriptive variables
file_name = sys.argv[1]
# Convert the search keyword to uppercase for case-insensitive matching
searched_keyword = sys.argv[2].upper()

# Validate if the source file exists before attempting to open it
if not os.path.exists(file_name):
    print(f"Error: The file '{file_name}' was not found!")
    sys.exit(1) # Terminate execution if the file is missing

try:
    # Open the source file for reading and the target file for writing using Context Managers
    # 'with' ensures that files are properly closed even if an error occurs
    with open(file_name, 'r', encoding='utf-8') as source_file:
        with open(output_file, "w", encoding="utf-8") as target_file:
            # Iterate through each line of the source file with a line counter starting from 1
            for line_number, line in enumerate(source_file, 1):
                 # Remove leading/trailing whitespaces and newline characters
                 line = line.strip()
                 
                 # Check if the keyword exists within the line (case-insensitive comparison)
                 if searched_keyword in line.upper():
                     # Write the formatted result: Line number and the content
                     target_file.write(f"Line {line_number}: {line}\n")
                     
    # Inform the user upon successful completion
    print(f"Success! Results saved to {output_file}")

except Exception as e:
    # Catch any unexpected errors (e.g., permission issues) and log the message
    print(f"An error occurred: {e}")
    sys.exit() # Safety exit