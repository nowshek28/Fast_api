import logging

from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:

    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self.model_name = settings.EMBEDDING_MODEL

        if self.provider == "huggingface":
            self.model = SentenceTransformer(self.model_name)

        else: 
            self.model = None

    def generate_embeddings(self, chunks: list[str]) -> list[list[float]]:
        """
        Generates embeddings for the given text using the specified provider and model.

        Args:
            chunks (list[str]): The input text chunks for which to generate embeddings.

        Returns:
            list[float]: A list of floating-point numbers representing the embeddings.
        """

        if self.provider == "huggingface":
            logger.info("Generating embeddings using Hugging Face model: %s", self.model_name)
            return self._generate_huggingface_embeddings(chunks)
        
        if self.provider == "openai":
            # return self._generate_openai_embeddings(text)
            logger.warning("OpenAI embedding provider is not implemented yet.")
            raise NotImplementedError("OpenAI embedding provider is not implemented yet.")
        
        raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def _generate_huggingface_embeddings(self, chunks: list[str]) -> list[list[float]]:
        
        """
        Generates embeddings using a Hugging Face model.
        """
        try:
            embeddings = self.model.encode(
                chunks,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            logger.info(" %d Embeddings generated successfully.", len(embeddings))
            return embeddings.tolist()
        
        except Exception as exc:
            logger.exception("Failed to generate embeddings using Hugging Face model.")
            raise RuntimeError("Embedding generation failed.") from exc