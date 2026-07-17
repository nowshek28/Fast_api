import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class ChunkService:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

    def chunk_text(self, text) -> list[str]:
        """
        Splits the given text into chunks based on the specified chunk size and overlap.
        """
        try:
            chunks = self.text_splitter.split_text(text)
            logger.info("Text chunking completed. Number of chunks created: %d", len(chunks))
            return chunks
        except Exception as e:
            logger.error("Error occurred during text chunking: %s", str(e))
            raise RuntimeError("Text chunking failed.") from e