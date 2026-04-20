numbers = [i for i in range(1, 11)]

squared = list(map(lambda x: x**2, numbers))
odd = list(filter(lambda x: x%2==1, numbers))

print(squared)
print(odd)