import os

path = r"c:\Users\KIET\OneDrive\Desktop\Geography\data\history_data.json"

with open(path, 'rb+') as f:
    f.seek(0, os.SEEK_END)
    # Check if ends with }
    pos = f.tell()
    f.seek(max(0, pos - 10))
    tail = f.read()
    print(f"Tail: {tail}")
    
    # We expect it to end with "    }" (no newline?) or "    }\n"
    # We want to add "\n  }\n}"
    
    f.write(b"\n  }\n}")
    print("Appended closing braces.")

# Verify
import json
try:
    data = json.load(open(path, encoding='utf-8'))
    print("JSON is now VALID.")
except Exception as e:
    print(f"JSON is still INVALID: {e}")
