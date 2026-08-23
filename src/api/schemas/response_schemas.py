from typing import Optional
from pydantic import BaseModel


class CollectionSchema(BaseModel):
    name: str
    size: Optional[int] = None
    distance: Optional[str] = None
    

class IndexSchema(BaseModel):
    name: str
