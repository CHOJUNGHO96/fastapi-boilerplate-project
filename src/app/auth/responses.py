from dataclasses import dataclass
from typing import Type

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ResponsJson(JSONResponse):
    @classmethod
    def extract_response_fields(cls, response_model: Type[BaseModel], entity: dataclass) -> JSONResponse:
        model_fields = response_model.model_fields
        entity_fields = entity.to_dict()

        mapping_keys = set(list(model_fields.keys())) & set(list(entity_fields.keys()))
        reonse_fields = {key: entity_fields[key] for key in mapping_keys}
        return JSONResponse(content=reonse_fields)
