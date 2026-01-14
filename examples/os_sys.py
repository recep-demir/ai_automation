import os

def scan_error_logs(directory_path):
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".log") or file_name.endswith(".txt"):
            file_path = os.path.join(directory_path, file)
            
            with open(file_path, "r", encoding = "utf-8") as file:
                content = file.readlines()
                for line_number, line in enumerate(content, 1):
                    if "ERRROR" in line.upper():
                        print(f"[ALERT] Found in {file_name} (Line {line_number}): {line.strip()}")

