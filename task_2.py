file_path = "server.log"
report_file = "error_report.txt"
search_word = "ERROR"

with open(file_path, "r", encoding="utf-8") as reader, \
     open(report_file, "w", encoding="utf-8") as writer:
    
    for line in reader:
        if search_word in line:
            writer.write(line)

print("islem tamamlandi:Hatalar ayiklandi.")