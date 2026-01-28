# coding=utf-8
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.auth.usecases.dto import LogoutCommand
from app.auth.usecases.logout_usecase import LogoutUseCase

router = APIRouter()


@router.post("/logout")
async def logout(
    request: Request,
    logout_usecase: LogoutUseCase = Depends(),
):
    """
    User logout endpoint.

    This endpoint:
    1. Executes logout business logic via LogoutUseCase
    2. Deletes authentication cookies
    3. Returns success response

    Note: Cookie deletion (HTTP concern) is handled here, not in UseCase.
    """
    # Step 1: Get user from request state (set by middleware)
    user_login_id = request.state.user.get("login_id") if hasattr(request.state, "user") else None

    # Step 2: Execute logout business logic (cache cleanup)
    if user_login_id:
        await logout_usecase.execute(LogoutCommand(login_id=user_login_id))

    # Step 3: Generate HTTP response and delete cookies (HTTP concern)
    response = JSONResponse(content={"status": 200, "msg": "Success Logout."})
    response.delete_cookie(key="token_type")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return response
