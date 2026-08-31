"""
embedder.py

Generates dense vector embeddings for text chunks and queries.
Supports local sentence-transformers models with automatic CPU/GPU device selection,
batching, L2 normalization, and cosine similarity calculations.
"""

import os
from typing import List, Union, Dict, Any
import numpy as np

from src.logger import get_logger

logger = get_logger(__name__)

# Default lightweight, high-performance open-source embedding model
# Dimensions: 384, Fast on CPU, excellent for semantic search
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:
    """
    Manages loading the embedding model and computing dense vector representations.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None

    @property
    def model(self):
        """Lazy load the model on first use so startup remains fast."""
        if self._model is None:
            logger.info(f"Loading embedding model: '{self.model_name}'...")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info(
                    f"Model '{self.model_name}' loaded successfully. "
                    f"Vector dimension: {self.dimension}"
                )
            except Exception as e:
                logger.error(f"Failed to load embedding model '{self.model_name}': {e}", exc_info=True)
                raise
        return self._model

    @property
    def dimension(self) -> int:
        """Returns the output vector dimensionality of the embedding model."""
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a single string (such as a search query).
        Returns a list of floats (L2-normalized).
        """
        if not text or not text.strip():
            return [0.0] * self.dimension

        vector = self.model.encode(
            text,
            normalize_embeddings=True,  # L2 normalization ensures dot product == cosine similarity
            show_progress_bar=False
        )
        return vector.tolist()

    def embed_batch(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Embeds a batch of texts efficiently using vectorized tensor operations.
        
        Args:
            texts: List of strings to embed.
            show_progress: Whether to display a progress bar.

        Returns:
            List of embedding vectors (each vector is a list of floats).
        """
        if not texts:
            return []

        logger.info(f"Embedding batch of {len(texts)} texts (batch_size={self.batch_size})...")
        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=show_progress
        )
        return vectors.tolist()

    def embed_chunks(
        self,
        chunks: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Takes a list of Chunk dicts, generates embeddings for their 'text' field,
        and returns enriched chunks with an 'embedding' key.
        """
        if not chunks:
            return []

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embed_batch(texts, show_progress=show_progress)

        enriched_chunks = []
        for chunk, emb in zip(chunks, embeddings):
            chunk_copy = dict(chunk)
            chunk_copy["embedding"] = emb
            enriched_chunks.append(chunk_copy)

        logger.info(f"Successfully embedded {len(enriched_chunks)} chunks.")
        return enriched_chunks

    @staticmethod
    def cosine_similarity(vec_a: Union[List[float], np.ndarray], vec_b: Union[List[float], np.ndarray]) -> float:
        """
        Computes cosine similarity between two vectors.
        Range: -1.0 to 1.0 (Higher is more semantically similar).
        """
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))
