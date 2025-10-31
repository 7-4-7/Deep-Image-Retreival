import torch

from helpers import _load_clip_model
from helpers import get_topk_records

class QueryHandler:
    def __init__(self):
        """Initializes the QueryHandler."""
        self.model, self.preprocessor = _load_clip_model()
        self.model.eval()

    def generate_clip_embeddings(self, search_phrase: str):
        """
        Takes in a search phrase and generates its CLIP text embedding.
        Normalizes the embedding for cosine similarity.
        """
        inputs = self.preprocessor(
            text=search_phrase,
            return_tensors="pt",
            padding=True
        )

        with torch.no_grad():
            text_embeds = self.model.get_text_features(**inputs)

        text_embeds = text_embeds / text_embeds.norm(p=2, dim=-1, keepdim=True)

        return text_embeds.cpu().numpy().tolist()
    
    def retrieve_top_k(self, q_emb, k):
        """Retrieves top k records from pinecone db"""
        result = get_topk_records(q_emb)['matches'] 
        images_to_show_list = []
        for entry in result:
            images_to_show_list.append(entry['metadata']['image_path'])
        return images_to_show_list
        
        
        
