from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, Request

from app.auth.facades.auth_facade import AuthFacade
from app.auth.model.user_model import ResponseTokenModel

router = APIRouter()


@router.get("/refresh_token", response_model=ResponseTokenModel)
@inject
async def refresh_token(
    request: Request,
    auth_facade: AuthFacade = Depends(),
):
    return await auth_facade.refresh_token(request)
