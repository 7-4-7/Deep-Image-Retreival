from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config

from pathlib import Path
from typing import List

from upload_pipeline import UploadPipeline
from query_handler_pipeline import QueryHandler
from models import SearchRequest
from config import SECRET_KEY

import logging
import colorlog
import os
import httpx


# =====================================
# LOGGING SETUP
# =====================================
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


# =====================================
# APP INITIALIZATION
# =====================================
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

config = Config(".env")
oauth = OAuth(config)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": (
            "openid email profile "
            "https://www.googleapis.com/auth/photoslibrary.readonly"
        )
    }
)


# =====================================
# STATIC FILES
# =====================================
app.mount("/photos", StaticFiles(directory="photos"), name="photos")


# =====================================
# ROUTES
# =====================================
@app.get("/")
def health_check():
    return {"message": "alive"}


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    # Force full consent & offline access
    return await google.authorize_redirect(
        request,
        redirect_uri,
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}


@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await google.authorize_access_token(request)
    user = await google.get("https://www.googleapis.com/oauth2/v2/userinfo", token=token)
    profile = user.json()
    request.session["token"] = token
    return {"user_profile": profile, "token": token}


@app.get("/debug_token")
async def debug_token(request: Request):
    token = request.session.get("token")
    if not token:
        return {"error": "Not authenticated"}
    return {
        "scope": token.get("scope", "NO SCOPE IN TOKEN"),
        "access_token_present": "access_token" in token
    }


# =====================================
# GOOGLE PHOTOS RETRIEVAL
# =====================================
@app.get("/drive_photos")
async def list_photos(request: Request):
    token = request.session.get("token")
    if not token:
        return {"error": "Not authenticated. Please visit /login first."}

    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            photos_resp = await client.post(
                "https://photoslibrary.googleapis.com/v1/mediaItems:search",
                headers=headers,
                json={"pageSize": 25}
            )

            photos_data = photos_resp.json()

            if "error" in photos_data:
                return {"api_error": photos_data["error"]}

            if "mediaItems" not in photos_data:
                return {"error": "No photos found in your Google Photos library."}

            image_urls = [
                {
                    "url": item["baseUrl"] + "=d",
                    "filename": item.get("filename", ""),
                    "mimeType": item.get("mimeType", "")
                }
                for item in photos_data["mediaItems"]
                if item.get("mimeType", "").startswith("image/")
            ]

            return {
                "photo_count": len(image_urls),
                "images": image_urls
            }

    except Exception as e:
        return {"error": str(e)}


# =====================================
# UPLOAD + RETRIEVAL PIPELINE
# =====================================
@app.post("/upload-image")
async def upload_image(files: List[UploadFile] = File(...)):
    logging.info("=" * 60)
    logging.info("Starting Upload Pipeline")
    logging.info("=" * 60)

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

    logging.info("=" * 60)
    logging.info("Upload Pipeline Complete")
    logging.info("=" * 60)

    return image_caption_pairs


@app.post("/search-endpoint")
async def search_endpoint(search_phrase: SearchRequest):
    q = QueryHandler()
    q_emb = q.generate_clip_embeddings(search_phrase.search_phrase)
    images_to_show = q.retrieve_top_k(q_emb=q_emb, k=5)
    return {"retrieved_images": images_to_show}
