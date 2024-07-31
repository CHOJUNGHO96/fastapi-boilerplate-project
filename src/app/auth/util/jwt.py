from datetime import datetime, timedelta

from jose import jwt


def create_access_token(
    jwt_secret_key: str,
    jwt_algorithm: str,
    user_id: int | None = None,
    login_id: str | None = None,
    user_name: str | None = None,
    user_type: int | None = None,
    expire: int | None = None,
) -> str:
    if expire:
        exp = datetime.utcnow() + timedelta(minutes=expire)
    else:
        exp = datetime.utcnow() + timedelta(minutes=60 * 24 * 8)
    to_encode = {
        "user_id": user_id,
        "user_name": user_name,
        "user_type": user_type,
        "login_id": login_id,
        "exp": exp,
    }

    encoded_jwt = jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)
    return encoded_jwt
