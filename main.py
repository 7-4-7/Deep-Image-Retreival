from fastapi import FastAPI, Request, UploadFile, File
from pathlib import Path
from typing import List

from upload_pipeline import UploadPipeline
from query_handler_pipeline import QueryHandler

import logging
import colorlog


formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    log_colors={
        "DEBUG":    "cyan",
        "INFO":     "green",
        "WARNING":  "yellow",
        "ERROR":    "red",
        "CRITICAL": "bold_red,bg_white",
    }
)
handler = colorlog.StreamHandler()

handler.setFormatter(formatter)

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


app = FastAPI()

@app.get('/')
def health_check():
    return {"message" : "alive"}

@app.post("/upload-image")
async def upload_image(files: List[UploadFile] = File(...)):
    logging.info("="*60)
    logging.info("Starting Upload Pipeline")
    logging.info("="*60)

    temp_dir = Path("photos/recent")
    persist_dir = Path("photos/all")


    p = UploadPipeline(temp_dir, persist_dir)
    
    p.store_images(files)

    logging.info("Step 1: Running captioning model")
    image_caption_pairs = p.run_captioning_model()
    logging.info(f"Captioning complete. Results: {len(image_caption_pairs)} pairs")

    logging.info("Step 2: Running embedding model")
    image_caption_emb_pairs = p.run_emebedding_model(image_caption_pairs)
    logging.info(f"Embedding complete. Results: {len(image_caption_emb_pairs)} pairs")

    logging.info("Step 3: Pushing to vector database")
    p.push_to_vector_db(image_caption_emb_pairs)

    logging.info("="*60)
    logging.info("Upload Pipeline Complete")
    logging.info("="*60)
    return image_caption_pairs

@app.post('/search-endpoint')
async def search_endpoint(search_phrase : str):
    """Endpoint that receives search text and performs operation on it"""
    # payload = await request.json()
    # search_phrase = payload['search_phrase']
    q = QueryHandler()
    q_emb = q.generate_clip_embeddings(search_phrase)
    images_to_show = q.retrieve_top_k(q_emb=q_emb, k = 5)
    return {'retreived images' : images_to_show}
    
    