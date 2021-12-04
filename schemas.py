from typing import List, Optional, Dict
from pydantic import BaseModel


# Request and Responses Schema
class DefaultResponse(BaseModel):
    status: Optional[str]
    message: Optional[str]


class EndPointBase(BaseModel):
    name: str
    owner: str


class EndPointCreate(EndPointBase):
    pass


class EndPoint(EndPointBase):
    id: int

    class Config:
        orm_mode = True


class PredictCreate(BaseModel):
    data: Dict = {}

    class Config:
        orm_mode = True


class PredictResponse(BaseModel):
    probability: Optional[float]
    label: Optional[str]
    request_id: Optional[int]
    response: Optional[DefaultResponse] = None


class ABTestCreate(BaseModel):
    title: str
    created_by: str
    parent_mlalgorithm1: int
    parent_mlalgorithm2: int

    class Config:
        orm_mode = True


class ABTestResponse(BaseModel):
    id: int
    response: Optional[DefaultResponse] = None


class StopABTestResponse(BaseModel):
    response: Optional[DefaultResponse] = None
    summary: Optional[str]


class MLRequestCreate(BaseModel):
    feedback: Optional[str]

    class Config:
        orm_mode = True


class MLRequestResponse(BaseModel):
    response: Optional[DefaultResponse] = None


