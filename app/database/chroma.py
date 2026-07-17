import logging

import chromadb

from app.core.config import settings

logger = logging.getLogger(__name__)

chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH
)

transcript_collection = chroma_client.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME
)

