import logging
import colorlog
from pathlib import Path
from PIL import Image

from helpers import push_to_pinecone, save_locally, save_s3, load_captioning_model, perform_captioning, move_files, call_clip_model

handler = colorlog.StreamHandler()

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
handler.setFormatter(formatter)

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class UploadPipeline:
    def  __init__(self, temp_store_dir, persist_dir):
        self.temp_dir = temp_store_dir
        self.persist_dir = persist_dir
        logging.info(f"UploadPipeline initialized with temp_dir={temp_store_dir}, persist_dir={persist_dir}")
        
    def store_images(self, files, cloud_save : bool = False,):
        """Store the uploaded image in cloud/locally, images are renamed to UUID"""
          
        logging.info("Backend Initiated")
        logging.info(f"Number of files to store: {len(files) if hasattr(files, '__len__') else 'unknown'}")
        
        if not(cloud_save):
            logging.info("Going with local storage")
            self.temp_dir.mkdir(exist_ok=True)
            save_locally(files, self.temp_dir)
        else:
            # USE AWS S3
            logging.info("Using cloud storage (AWS S3)")
            save_s3(files)   
            
        logging.info("Uploaded Images Stored Successfully")
        
    def run_captioning_model(self,):
        """Runs a gemini model to generate captions for all the image stored in recent"""
        logging.info("Intiating captioning process")
        
        # Count images in temp_dir
        if self.temp_dir.exists():
            image_count = len(list(self.temp_dir.iterdir()))
            logging.info(f"Found {image_count} images in temp directory")
        else:
            logging.warning(f"Temp directory does not exist: {self.temp_dir}")
        
        model = load_captioning_model()
        logging.info("Captioning model loaded successfully")
        
        img_caption_pairs = perform_captioning(model, self.temp_dir)
        logging.info(f"Generated captions for {len(img_caption_pairs)} images")
        
        logging.info("Emptying recent dir")
        move_files(self.temp_dir, persist_dir)
        logging.info(f"Moved files from {self.temp_dir} to {persist_dir}")
        
        logging.info("Terminating Captioning Process")
        return img_caption_pairs
    
    def run_emebedding_model(self, img_caption_pairs):
        """Takes in image and it's caption and runs clip model to generate embeddings, aggregrating the final embedding into one"""
        img_caption_emb_pairs = {}
        logging.info("Initiating Embedding Creation")
        logging.info(f"Processing {len(img_caption_pairs)} image-caption pairs")
        
        for idx, key in enumerate(img_caption_pairs, 1):
            img_path = self.persist_dir / key
            img_captions = img_caption_pairs[key]
            
            logging.debug(f"[{idx}/{len(img_caption_pairs)}] Processing: {key}")
            logging.debug(f"  Image path: {img_path}")
            logging.debug(f"  Captions: {img_captions}")
            
            aggregate_embedding = call_clip_model(img_path, img_captions)
            
            logging.debug(f"  Embedding shape: {aggregate_embedding.shape if hasattr(aggregate_embedding, 'shape') else 'unknown'}")
            
            img_caption_emb_pairs[img_path] = [
                img_captions,
                aggregate_embedding
            ]
            
        logging.info(f"Created embeddings for {len(img_caption_emb_pairs)} images")
        logging.info("Terminating Embedding Creation")
        return img_caption_emb_pairs
        
    def push_to_vector_db(self, img_caption_emb_pairs):
        logging.info("Initiating Vector DB operations")
        logging.info(f"Preparing to push {len(img_caption_emb_pairs)} records to Pinecone")
        
        # Log sample of data being pushed
        if img_caption_emb_pairs:
            sample_key = list(img_caption_emb_pairs.keys())[0]
            sample_value = img_caption_emb_pairs[sample_key]
            logging.debug(f"Sample record:")
            logging.debug(f"  Key type: {type(sample_key).__name__}")
            logging.debug(f"  Key value: {sample_key}")
            logging.debug(f"  Captions type: {type(sample_value[0]).__name__}")
            logging.debug(f"  Embedding type: {type(sample_value[1]).__name__}")
            if hasattr(sample_value[1], 'shape'):
                logging.debug(f"  Embedding shape: {sample_value[1].shape}")
        
        try:
            push_to_pinecone(img_caption_emb_pairs)
            logging.info("✅ Successfully pushed vectors to Pinecone")
        except Exception as e:
            logging.error(f"❌ Exception Happened: {e}")
            logging.error(f"Exception type: {type(e).__name__}")
            import traceback
            logging.debug("Full traceback:")
            logging.debug(traceback.format_exc())

# temp_dir = Path('photos//recent')
# persist_dir = Path('photos//all')
# p = UploadPipeline(temp_dir, persist_dir)
# image_caption_pairs = p.run_captioning_model()
# print(image_caption_pairs)
# image_caption_emb_pairs = p.run_emebedding_model(image_caption_pairs)
# print(image_caption_emb_pairs)

logging.info("="*60)
logging.info("Starting Upload Pipeline")
logging.info("="*60)

temp_dir = Path("photos/recent")
persist_dir = Path("photos/all")

p = UploadPipeline(temp_dir, persist_dir)

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