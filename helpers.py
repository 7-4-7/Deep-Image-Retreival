import uuid
import os
import shutil
from pathlib import Path
from google import genai
from config import client, pc, INDEX_NAME, INDEX_HOST
from prompts import CAPTIONING_PROMPT_BETA
from parsers import json_parser
import logging
import pathlib
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec


def save_locally(files, save_dir):
    """Saves files in local directory"""
    for file in files:
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = save_dir / unique_name
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

def save_s3(files):
    """Saves files in cloud AWS S3 bucket"""
    pass

def load_captioning_model():
    return client

def perform_captioning(model, img_dir):
    """Performs captioning on images stored in recent dir"""
    img_captioning_pairs = {}
    if type(img_dir) == pathlib.WindowsPath: 
        for file in img_dir.iterdir():
            logging.debug('Running')
            img = Image.open(file)
            reponse = client.models.generate_content(
                model = "gemini-2.5-flash",
                contents = [img, CAPTIONING_PROMPT_BETA]
            )
            parsed_response = json_parser(reponse.text)
            img_captioning_pairs[file.name] = parsed_response['captions']
    
    else:
        # cloud recent dir
        pass
    
    return img_captioning_pairs

def move_files(source, dest):
    """Empties recent dir and moves the contents to dest"""
    if type(source) == pathlib.WindowsPath:
        for item in source.iterdir():
            target_path = dest / item.name
            shutil.move(str(item), str(target_path))

def _load_clip_model():
    """Loads clip model and preprocessor"""
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor

def call_clip_model(img_path, img_captions):
    model, processor = _load_clip_model()
    img = Image.open(img_path)
    inputs = processor(text = img_captions,
                       images = img,
                       return_tensors = "pt",
                       padding = True)
    with torch.no_grad():
        outputs = model(**inputs)
        image_embeds = outputs.image_embeds
        text_embeds = outputs.text_embeds
        image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
        text_embeds = text_embeds / text_embeds.norm(p=2, dim=-1, keepdim=True)
        mean_text_embed = text_embeds.mean(dim=0, keepdim=True)
        combined_embed = (image_embeds + mean_text_embed) / 2
        combined_embed = combined_embed / combined_embed.norm(p=2, dim=-1, keepdim=True)
    # sim = torch.cosine_similarity(image_embeds, combined_embed)
    # print(sim)
    return combined_embed.squeeze(0)
   
def get_topk_records(q_emb):
    index = pc.Index(host=INDEX_HOST)
    matches = index.query(
                    namespace="__default__",
                    vector=q_emb, 
                    top_k=5,
                    include_metadata=True,
                    include_values=False
                )
    return matches

         
def push_to_pinecone(records):
    index_list = pc.list_indexes()
    existing_names = [idx['name'] for idx in index_list]

    if INDEX_NAME not in existing_names:
        pc.create_index(
            name=INDEX_NAME,
            dimension=512,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            deletion_protection="disabled"
        )
        print("INDEX CREATED")
    else:
        print("Index already exists, skipping creation.")
    
    index = pc.Index(INDEX_NAME)
    vectors = []
    for image_path, (captions, embedding) in records.items():
        vectors.append({
            "id": str(image_path.name),  
            "values": embedding.tolist(), 
            "metadata": {"captions": captions,
                         "image_path" : str(image_path),}
        })

    index.upsert(vectors=vectors)
    print(f"{len(vectors)} vectors inserted into {INDEX_NAME}.")
