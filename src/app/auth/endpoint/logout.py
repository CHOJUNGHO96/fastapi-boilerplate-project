from fastapi import APIRouter, Depends

from app.auth.services.auth_facade import AuthFacade

router = APIRouter()


@router.post("/logout")
async def logout(
    auth_facade: AuthFacade = Depends(),
):
    response = await auth_facade.logout()
    return response
