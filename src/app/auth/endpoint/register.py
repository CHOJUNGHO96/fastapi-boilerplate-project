# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.auth.model.request import RequestRegisterModel
from app.auth.usecases.dto import RegisterUserCommand
from app.auth.usecases.register_user_usecase import RegisterUserUseCase

router = APIRouter()


@router.post("/register")
@inject
async def register(request_user_info: RequestRegisterModel, register_usecase: RegisterUserUseCase = Depends()):
    """
    User registration endpoint.

    This endpoint:
    1. Executes registration business logic via RegisterUserUseCase
    2. Generates HTTP response with success message

    Note: HTTP response formatting is handled here, not in UseCase.
    """
    # Step 1: Execute registration business logic
    result = await register_usecase.execute(
        RegisterUserCommand(
            login_id=request_user_info.login_id,
            user_name=request_user_info.user_name,
            password=request_user_info.password,
            email=request_user_info.email,
            user_type=request_user_info.user_type,
        )
    )

    # Step 2: Generate HTTP response
    return JSONResponse(
        content={
            "status": 200,
            "msg": "Success Register.",
            "user_id": result.user_id,
            "login_id": result.login_id,
        }
    )
