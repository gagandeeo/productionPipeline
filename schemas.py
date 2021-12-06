from typing import List, Optional, Dict
from pydantic import BaseModel


# Request and Responses Schema

# Default Response
class DefaultResponse(BaseModel):
    status: Optional[str]
    message: Optional[str]


# predict
class PredictCreate(BaseModel):
    data: Dict = {}

    class Config:
        orm_mode = True


class PredictResponse(BaseModel):
    probability: Optional[float]
    label: Optional[str]
    request_id: Optional[int]
    response: Optional[DefaultResponse] = None


# add_abtest
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


# stop_abtest
class StopABTestResponse(BaseModel):
    response: Optional[DefaultResponse] = None
    summary: Optional[str]


# put_mlrequest
class MLRequestCreate(BaseModel):
    feedback: Optional[str]

    class Config:
        orm_mode = True


class MLRequestResponse(BaseModel):
    response: Optional[DefaultResponse] = None


# query and values
class QueryParams(BaseModel):
    data: Optional[Dict] = {}


class Values(BaseModel):
    data: Optional[Dict] = {}

