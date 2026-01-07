file_path = "server.log"
error_list = []
search_word = "ERROR"


with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        if search_word in line:
            error_list.append(line.strip())

print(error_list)