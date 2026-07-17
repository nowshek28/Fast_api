from pydantic import BaseModel

class VectorRecord(BaseModel):
    id: str
    document: str
    embedding: list[float]
    metadata: dict