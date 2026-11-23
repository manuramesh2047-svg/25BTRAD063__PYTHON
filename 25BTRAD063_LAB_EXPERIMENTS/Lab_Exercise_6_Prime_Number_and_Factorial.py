# Lab Exercise 6 - Prime Number and Factorial

# Prime Number Program
num = int(input("Enter a number: "))

if num <= 1:
    print(num, "is not a prime number")
else:
    prime = True
    for i in range(2, num):
        if num % i == 0:
            prime = False
            break
    if prime:
        print(num, "is a prime number")
    else:
        print(num, "is not a prime number")

# Factorial Program
n = int(input("\nEnter a number to find factorial: "))
factorial = 1
for i in range(1, n + 1):
    factorial = factorial * i
print("Factorial of", n, "is", factorial)
