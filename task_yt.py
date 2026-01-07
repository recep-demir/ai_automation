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

file_path = 'student_records.txt'

with open (file_path, "w", encoding="utf-8") as file:
    file.write("user Name: John Doe\n")
    file.write("Department: Computer Science\n")

    additional_info = ["Level:Advanced\n", "Status:Active\n"]
    file.writelines(additional_info)