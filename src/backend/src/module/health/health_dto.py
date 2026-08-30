from typing import Literal

from pydantic import BaseModel


class LivenessResponseDTO(BaseModel):
    status: Literal["ok"] = "ok"
    message: str 
