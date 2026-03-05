import os

path = r"C:\uni programming\Python PP2\python-practice\text6.txt"

with open(path, "w", encoding="utf-8") as f:
    f.write("Это 1 строка")
    f.write("строка")
    f.write("Это 3 строка")
    f.write("Это 4 строка")

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())

