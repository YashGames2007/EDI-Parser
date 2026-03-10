from pydantic import BaseModel
from typing import List, Optional


class Element(BaseModel):

    column: int
    value: str


class Segment(BaseModel):

    row: int
    segment_id: str
    elements: List[Element]


class Metadata(BaseModel):

    sender_id: Optional[str]
    receiver_id: Optional[str]
    transaction_type: Optional[str]


class ValidationError(BaseModel):

    code: str
    description: str


class ParseResponse(BaseModel):

    metadata: Metadata
    parsed_data: List[Segment]
    errors: List[ValidationError]