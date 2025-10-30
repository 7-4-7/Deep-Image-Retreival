from google import genai
import os
from dotenv import load_dotenv  
from prompts import CAPTIONING_PROMPT
from PIL import Image
from pathlib import Path


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



root_dir = Path('photos//recent//bharat.png')
root_dir.unlink()
# print(root_dir.exist)
# image = Image.open(root_dir)
# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=[image, CAPTIONING_PROMPT]
# )
# print(response.text)
