# coding=utf-8
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    class Config:
        @staticmethod
        def json_schema_extra(schema: dict, _):
            props = {}
            for k, v in schema.get("properties", {}).items():
                if not v.get("hide", False):
                    props[k] = v
            schema["properties"] = props
