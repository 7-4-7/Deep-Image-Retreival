from google import genai
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "deep-image-retriever"
INDEX_HOST = "https://deep-image-retriever-wvoooip.svc.aped-4627-b74a.pinecone.io"

SECRET_KEY = os.getenv('SECRET_KEY')
