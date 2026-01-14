import os

current_location = os.getcwd()
print(f"Current Location: {current_location}")

folder_name = "SystemLogs"
target_path = os.path.join(current_location, "tasks", "task_3",folder_name)
print(f"Target Path: {target_path}")

# full_path = os.path.join(target_path, )

if not os.path.exists(target_path):
    os.makedirs(target_path)
    print(f"{folder_name} folder created successfully.")
else:
    print(f"{folder_name} folder already exists")


    files = os.listdir(".")
    for file in files:
        print(file)