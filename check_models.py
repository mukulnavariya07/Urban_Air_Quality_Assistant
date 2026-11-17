
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found.")
else:
    try:
        client = genai.Client(api_key=api_key)

        print("Checking available Gemini models...\n")

        for model in client.models.list():
            name = model.name or ""

            if "flash" in name.lower():
                print(name)

    except Exception as e:
        print("Error:", e)
