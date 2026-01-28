from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.auth.model import ResponseTokenModel
from app.auth.responses import ResponsJson
from app.auth.usecases.dto import RefreshTokenCommand
from app.auth.usecases.refresh_token_usecase import RefreshTokenUseCase

router = APIRouter()


@router.get("/refresh_token", response_model=ResponseTokenModel)
@inject
async def refresh_token(
    request: Request,
    refresh_token_usecase: RefreshTokenUseCase = Depends(),
):
    """
    Token refresh endpoint.

    This endpoint:
    1. Validates refresh_token exists in cookies
    2. Executes token refresh business logic via RefreshTokenUseCase
    3. Generates HTTP response with new tokens
    4. Updates authentication cookies

    Note: Middleware has already validated the refresh_token and populated request.state.user.
    """
    # Step 1: Validate refresh_token in cookies (HTTP concern)
    if "refresh_token" not in request.cookies:
        return JSONResponse(status_code=422, content={"status": 422, "msg": "Token not in cookie"})

    # Step 2: Execute token refresh business logic
    result = await refresh_token_usecase.execute(
        request, RefreshTokenCommand(refresh_token=request.cookies["refresh_token"])
    )

    # Step 3: Generate HTTP response (Presentation logic)
    response: JSONResponse = ResponsJson.extract_response_fields(response_model=ResponseTokenModel, entity=result.user)

    # Step 4: Update HTTP cookies (HTTP concern) with security flags
    response.set_cookie(
        "token_type",
        result.token_type,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    response.set_cookie(
        "access_token",
        result.access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=15 * 60,  # 15 minutes
    )
    response.set_cookie(
        "refresh_token",
        result.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=3000 * 60,  # 3000 minutes
    )

    return response
