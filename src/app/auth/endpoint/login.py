# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.facades.auth_facade import AuthFacade
from app.auth.model import ResponseLoginModel

router = APIRouter()


@router.post("/login", response_model=ResponseLoginModel)
@inject
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_facade: AuthFacade = Depends(),
):
    response: JSONResponse = await auth_facade.login(request, username=form_data.username, password=form_data.password)
    return response
