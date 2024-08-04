from dependency_injector.wiring import inject
from fastapi import APIRouter, Request, Depends
from app.auth.facades.auth_facade import AuthFacade

router = APIRouter()


@router.get("/refresh_token")
@inject
async def refresh_token(
    request: Request,
    auth_facade: AuthFacade = Depends(),
):
    return auth_facade.refresh_token(request)
