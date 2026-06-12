from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    message: str
    data: T


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
