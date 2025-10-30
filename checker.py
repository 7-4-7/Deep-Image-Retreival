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

from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

# Load model + processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model.eval()

image = Image.open("example.jpg")

# Preprocess image to match CLIP’s expected input (224x224, normalized)
inputs = processor(images=image, return_tensors="pt")

# Forward pass
with torch.no_grad():
    image_features = model.get_image_features(**inputs)

# Normalize to unit length (important for cosine similarity)
image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

print(image_features.shape)  # → torch.Size([1, 512])


texts = ["a cat sitting on a sofa", "a dog running in the park"]

# Preprocess text
inputs = processor(text=texts, return_tensors="pt", padding=True)

# Forward pass
with torch.no_grad():
    text_features = model.get_text_features(**inputs)

# Normalize
text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)

print(text_features.shape)  # → torch.Size([2, 512])



