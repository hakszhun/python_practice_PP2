a, b = input().split()
a = int(a)
b = int(b)

def squares_generator(start, end):
    for i in range(start, end+1):
        squared = i**2
        yield squared

gen = squares_generator(a, b)

for num in gen:
    print(num)