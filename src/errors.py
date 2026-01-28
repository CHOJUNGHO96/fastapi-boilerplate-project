class StatusCode:
    HTTP_500 = 500
    HTTP_400 = 400
    HTTP_401 = 401
    HTTP_403 = 403
    HTTP_404 = 404
    HTTP_405 = 405
    HTTP_409 = 409


class ErrorCode:
    """
    API 에러 코드 상수 정의.

    Enhancement #2: Centralized error code management
    에러 코드를 중앙에서 관리하여 명확성과 유지보수성을 향상
    """

    # 인증 에러 (401xxxx)
    NOT_AUTHORIZATION = 4010001  # 인증 필요
    EXPIRE_JWT_TOKEN = 4010002  # 토큰 만료
    NOT_FOUND_USER = 4010003  # 사용자 없음
    BAD_PASSWORD = 4010004  # 잘못된 비밀번호
    DUPLICATE_USER = 4010005  # 중복 사용자
    INVALID_JWT_TOKEN = 4010006  # 잘못된 토큰

    # 유효성 검증 에러 (400xxxx)
    VALIDATION_ERROR = 4000001  # 유효성 검증 실패

    # 내부 서버 에러 (500xxxx)
    INTERNAL_SQL_ERROR = 5000001  # SQL 오류
    INTERNAL_QUERY_ERROR = 5000002  # Query 오류

    # 향후 확장 가능
    # PERMISSION_DENIED = 4010007  # 권한 없음
    # ACCOUNT_LOCKED = 4010008  # 계정 잠김
    # RATE_LIMIT_EXCEEDED = 4290001  # 요청 한도 초과


class APIException(Exception):
    status_code: int
    code: str
    msg: str
    ex: Exception

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_500,
        code: str = "0000",
        msg: str = "",
        ex: Exception = Exception(),
    ):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.ex = ex
        super().__init__(ex)


class NotAuthorization(APIException):
    def __init__(self, ex: Exception = Exception()):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            code=str(ErrorCode.NOT_AUTHORIZATION),
            msg="Not Authorization",
            ex=ex,
        )


class ExpireJwtToken(APIException):
    def __init__(self, ex: Exception = Exception()):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            code=str(ErrorCode.EXPIRE_JWT_TOKEN),
            msg="Expire JWT Token",
            ex=ex,
        )


class NotFoundUserEx(APIException):
    def __init__(self, ex: Exception = Exception()):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            msg="해당 유저를 찾을 수 없습니다.",
            code=str(ErrorCode.NOT_FOUND_USER),
            ex=ex,
        )


class BadPassword(APIException):
    def __init__(self, ex: Exception = Exception()):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            msg="Bad password",
            code=str(ErrorCode.BAD_PASSWORD),
            ex=ex,
        )


class DuplicateUserEx(APIException):
    def __init__(self, ex: Exception = Exception(), user_id=""):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            code=str(ErrorCode.DUPLICATE_USER),
            msg=f"ID가 {user_id}인 유저가 존재합니다.",
            ex=ex,
        )


class InvalidJwtToken(APIException):
    def __init__(self, ex: Exception = Exception()):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            code=str(ErrorCode.INVALID_JWT_TOKEN),
            msg="Invalid JWT Token",
            ex=ex,
        )


class InternalSqlEx(APIException):
    def __init__(self, ex: Exception = Exception()):
        super().__init__(
            code=str(ErrorCode.INTERNAL_SQL_ERROR),
            msg="SQL error",
            ex=ex,
        )


class InternalQuerryEx(APIException):
    def __init__(self, ex: Exception = Exception()):
        super().__init__(
            code=str(ErrorCode.INTERNAL_QUERY_ERROR),
            msg="Query error",
            ex=ex,
        )


class ValidationError(APIException):
    def __init__(self, msg: str = "Validation error", ex: Exception = Exception()):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            code=str(ErrorCode.VALIDATION_ERROR),
            msg=msg,
            ex=ex,
        )
