from pydantic import BaseModel, Field


class QuerySchema(BaseModel):
    query: str = Field(..., min_length=1, description="Введите поисковый запрос")
    collection_name: str = Field(
        ..., min_length=1, description="Введите название коллекции"
    )


class AddCollectionSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название коллекции")


class AddIndexSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название индекса")
