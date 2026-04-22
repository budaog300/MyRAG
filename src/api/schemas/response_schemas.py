from pydantic import BaseModel


class CollectionSchema(BaseModel):
    name: str


class IndexSchema(BaseModel):
    name: str
