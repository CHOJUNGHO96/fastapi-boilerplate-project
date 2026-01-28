# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.model import ResponseLoginModel
from app.auth.responses import ResponsJson
from app.auth.usecases.dto import LoginCommand
from app.auth.usecases.login_usecase import LoginUseCase

router = APIRouter()


@router.post("/login", response_model=ResponseLoginModel)
@inject
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    login_usecase: LoginUseCase = Depends(),
):
    """
    User login endpoint.

    This endpoint:
    1. Executes login business logic via LoginUseCase
    2. Generates HTTP response with user data
    3. Sets authentication cookies

    Note: HTTP concerns (cookies) are handled here, not in UseCase.
    """
    # Step 1: Execute login business logic
    result = await login_usecase.execute(
        request, LoginCommand(login_id=form_data.username, password=form_data.password)
    )

    # Step 2: Generate HTTP response (Presentation logic)
    response: JSONResponse = ResponsJson.extract_response_fields(response_model=ResponseLoginModel, entity=result.user)

    # Step 3: Set HTTP cookies (HTTP concern) with security flags
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
