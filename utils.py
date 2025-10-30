import os
import uuid
import shutil
import dotenv
from google import genai
from prompts import CAPTIONING_PROMPT
from PIL import Image
from pathlib import Path
from parsers import json_parser
from transformers import CLIPProcessor, CLIPModel
import torch


dotenv.load_dotenv()

class Pipeline:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    def _load_clip_model():
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        image = Image.open("photos/recent/sample.png")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)


        return clip_model
    def _empty_folder(root_dir):
        """Empties folder files once operation is completed"""
        for path in root_dir.iterdir():
            try:
                path.unlink()
            except:
                print("Error Happened While Deleting")
        
        print("========="*5,"RECENT FOLDER EMPTIED","========="*5)
    def _transfer_file_content(source_dir, destination_folder ):
        """Copy the files form recent to all"""
        for file_path in source_dir.glob("*.*"):
            shutil.copy(file_path, destination_folder / file_path.name)
        print("========="*5,"FILE COPIED","========="*5)     
    def upload_image_logic(files, ):
        """Save it on recents"""
        save_dir = Path("photos//recent")
        save_dir.mkdir(exist_ok=True)

        for file in files:
            ext = os.path.splitext(file.filename)[1]
            unique_name = f"{uuid.uuid4()}{ext}"
            file_path = save_dir / unique_name

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
    def caption_image(self):
        """Generates captions per image and stores them"""
        recent_dir = Path('photos//recent')
        all_dir = Path('photos//all')
        paths = recent_dir.glob('*.png')
        img_caption_pair = {}
        for current,path in enumerate(paths):
            img = Image.open(path)
            response = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[img, CAPTIONING_PROMPT]
                    )
            print("========="*5,"CAPTION GENERATED [",current+1,"/", (len(paths)),"] PARSED", "========="*5)
            parsed_response = json_parser(response, current+1, len(paths))
            img_caption_pair[path.name] = parsed_response['captions'] ########
        # Push to all
        self._transfer_file_content(recent_dir, all_dir)
        # delete recent contents
        self._empty_folder(recent_dir)
        return img_caption_pair
        
    def generate_embedding_captions(img_caption_pair : dict):
        """Loads the clip model and generates embedding"""
        embeddings = {}
        for img_name, captions in img_caption_pair.items():
            
        
            
            
                                
        