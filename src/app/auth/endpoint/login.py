from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.model.user_model import ModelTokenData
from app.auth.services.auth_facade import AuthFacade

router = APIRouter()


@router.post("/login", response_model=ModelTokenData)
@inject
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_facade: AuthFacade = Depends(),
):
    response: JSONResponse = await auth_facade.login(request, username=form_data.username, password=form_data.password)
    return response
