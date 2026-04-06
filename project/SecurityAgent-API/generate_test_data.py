import csv
import random

FILENAME = "test_logs.csv"

normal_logs = [
    " - 192.168.1.10 - ERROR - Database connection timeout",
    " - 10.0.0.5 - ERROR - User logoff due to inactivity",
    " - 172.16.0.22 - ERROR - Invalid password attempt", 
    " - 192.168.1.15 - ERROR - Disk space nearly full",
    " - 192.168.1.10 - ERROR - API Gateway timeout",
]


def generate_brute_force(ip, start_time_second):
    logs = []
    for i in range(5):
        timestamp = f"2024-04-01 12:00:{start_time_second + (i * 5):02d}"
        logs.append([f"{timestamp} - {ip} - ERROR - Invalid password attempt", 1])
    return logs

def generate_dataset():
    dataset = []
    

    dataset.extend(generate_brute_force("192.168.1.50", 10))
    dataset.extend(generate_brute_force("10.0.0.99", 30))
    
    for i in range(40):
        timestamp = f"2024-04-01 13:{random.randint(10,59)}:{random.randint(10,59)}"
        log_content = random.choice(normal_logs)
        dataset.append([f"{timestamp}{log_content}", 0])

    random.shuffle(dataset)

    with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["log_line", "label"]) # Header
        writer.writerows(dataset)

    print(f"✅ Success! {FILENAME} generated with 50 logs (10 Attack / 40 Normal).")

if __name__ == "__main__":
    generate_dataset()