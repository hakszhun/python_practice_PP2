path = r"C:\uni programming\Python PP2\python-practice\Practice1\python-basics\test5.txt"

with open(path, "w", encoding="utf-8") as f:
    f.write("new place")

with open(path, "a", encoding="utf-8") as f:
    f.write("\nNew line added")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()
    print(content)