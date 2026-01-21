import re

line = "2026-01-20 14:05:30 ERROR 192.168.1.1 Connection lost"

# Regex Pattern (Parantezlere dikkat!)
pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"

match = re.search(pattern, line)

if match:
    # group(0) -> Eşleşen tüm metni verir (Bazen parantez dışı kısımlar da olabilir)
    print(f"Full Match: {match.group(0)}") 
    
    # group(1) -> SADECE ilk parantez içindeki veriyi verir
    print(f"Captured Group 1: {match.group(1)}")

