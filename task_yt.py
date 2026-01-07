# weight_p = int(input("Weight(pounds): "))
# weight_kg = 0.4536 * weight_p
# print(weight_kg)

# first = 'John'
# last = 'Smith'
# message = first + ' [' + last + '] is a code '
# msg = f'{first} [{last}] is a coder'
# print (message)
# print (msg)

# number = int(input ("Please enter a number : "))

# if number > 10 :
#     print("entered big number")

# else :
#     print("entered small number")

file_path = "shopping_list.txt"

with open (file_path,"w", encoding="utf-8") as file:
    market_list = ["egg\n", "honey\n", "bread\n"]
    file.writelines(market_list)

with open (file_path, "a", encoding="utf-8") as file:
    file.write("milk\n")

with open (file_path, "r", encoding="utf-8") as file:
    content = file.read()
    print(content)