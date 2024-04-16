from typing import Dict, Optional, List

from pydantic import BaseModel, Field

DataPayload = Dict[str, Dict[str, List[str]]]

SetDataPayload = Dict[str, Dict[str, Dict[str, float]]]


class InitializationResponse(BaseModel):
    status: str
    instance_id: Optional[str] = None


class ResponseData(BaseModel):
    status: str = Field(..., example="success")
    data: Dict[str, Dict[str, Dict[str, float]]]
