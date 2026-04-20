names = ["Alice", "Bob", "Charlie"]
for index, name in enumerate(names, start = 1):
    print(f"{index}: {name}")


keys = ["name", "age"]
values = ["Alice", 25]
person = dict(zip(keys, values))
print(person)