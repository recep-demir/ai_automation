# # # name = "John"
# # # character_age = "35"

# # # print(name.lower())
# # # print(len(name))
# # # print(name.index("o"))

# # age = 50
# # gpa = 3.7

# # print(pow(2,3))
# # print(2**3)
# # print(round(gpa))
# # print(max(7,3))

# # name = input("What is your name? ")
# # print("Hello " + name)

# num1 = input("Enter a number: ")
# num2 = input("Enter another number: ")
# result = float(num1) + float(num2)
# print(result)


sayilar = [12, 5, 8, 19, 3, 20, 2, 14, 7, 6]
# Görevin: Bu listedeki çift sayıları bulan, karelerini alan ve büyükten küçüğe sıralayan o tek satırlık List Comprehension kodunu yaz.

result = sorted([x**2 for x in sayilar if x%2==0],reverse=True)
print(result)