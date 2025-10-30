from fastapi import FastAPI, Request, UploadFile, File
from pathlib import Path
from typing import List
from utils import upload_image_logic

app = FastAPI()

@app.get('/')
def health_check():
    return {"message" : "alive"}

@app.post("/upload-image")
async def upload_image(files: List[UploadFile] = File(...)):
    upload_image_logic(files)
    return {"uploaded_files": '4040'}