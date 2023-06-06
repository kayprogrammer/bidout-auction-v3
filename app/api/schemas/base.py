from pydantic import BaseModel as RealBaseModel, validator
from asyncpg.pgproto.pgproto import UUID


class ResponseSchema(RealBaseModel):
    status: str = "success"
    message: str


class BaseModel(RealBaseModel):
    @validator(
        "*"
    )  # Aside from converting uuids to str, this validator helps load relationship column value while using from_orm
    def convert_uuid(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
