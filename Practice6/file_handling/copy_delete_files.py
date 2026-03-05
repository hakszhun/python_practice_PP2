import os

path = r"C:\uni programming\Python PP2\python-practice\text6.txt"

with open(path, "w", encoding="utf-8") as f:
    f.write("new file that is gonna be deleted")

if os.path.exists("text6.txt"):
    print("file exists")
    os.remove("text6.txt")
    print(f"file {f.name} was deleted")
else:
    print("file not found")


