import os
from pathlib import Path

items = os.listdir()
for item in items:
    print(item.strip())
