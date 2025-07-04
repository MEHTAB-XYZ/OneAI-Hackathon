import os
from dotenv import load_dotenv
from huggingface_hub import HfApi

load_dotenv()  # loads from .env

token = os.getenv("HF_TOKEN")
api = HfApi(token=token)
user = api.whoami()

print(f"✅ Token is valid! Logged in as: {user['name']}")
# I love Jim Halper and Pam Beesly from The Office.