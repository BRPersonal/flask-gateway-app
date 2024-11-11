import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TYK_AUTHORIZATION = os.getenv("X-TYK-AUTHORIZATION")
TYK_BASE_URL = os.getenv("TYK_BASE_URL")
print(f"authorization={TYK_AUTHORIZATION}")
print(f"baseUrl={TYK_BASE_URL}")


