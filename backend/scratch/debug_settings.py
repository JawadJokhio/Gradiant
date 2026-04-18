import os
from app.core.config import settings

print(f"Current Working Directory: {os.getcwd()}")
print(f"HF_API_KEY from settings: '{settings.hf_api_key}'")
print(f"GROQ_API_KEY from settings: '{settings.groq_api_key}'")

if settings.hf_api_key:
    print("HF Key is present!")
else:
    print("HF Key is MISSING!")
