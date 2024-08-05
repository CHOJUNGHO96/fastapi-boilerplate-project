# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends

from app.auth.facades.auth_facade import AuthFacade
from app.auth.model.request import RequestRegisterModel

router = APIRouter()


@router.post("/register")
@inject
async def register(request_user_info: RequestRegisterModel, auth_facade: AuthFacade = Depends()):
    return await auth_facade.register(request_user_info)
