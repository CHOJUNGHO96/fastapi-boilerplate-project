from typing import Annotated

from pydantic import Field

from model import BaseModel


class ModelTokenData(BaseModel):
    user_id: Annotated[int, Field(example="유저번호")]
    token_type: Annotated[str, Field(example="토큰타입")]
    access_token: Annotated[str, Field(example="토큰")]
    refresh_token: Annotated[str, Field(example="리프레시토큰")]
