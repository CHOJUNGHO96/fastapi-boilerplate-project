import ast
import json
import logging
from datetime import datetime, timedelta
from time import time

from fastapi.logger import logger
from fastapi.requests import Request

logger.setLevel(logging.INFO)
logging.getLogger("passlib").setLevel(logging.ERROR)


class LogAdapter:
    def __init__(self, request: Request, response=None, error=None):
        self.request = request
        self.response = response
        self.error = error

    async def process(self, request: Request, response=None, error=None):
        time_format = "%Y/%m/%d %H:%M:%S"
        t = time() - request.state.start
        status_code = error.status_code if error else response.status_code
        error_log = None
        user: dict | None = request.state.user if request.state.user else None
        if isinstance(user, str):
            user = ast.literal_eval(user)

        if error:
            if request.state.inspect:
                frame = request.state.inspect
                error_file = frame.f_code.co_filename
                error_func = frame.f_code.co_name
                error_line = frame.f_lineno
            else:
                error_func = error_file = error_line = "UNKNOWN"

            error_log = dict(
                errorFunc=error_func,
                location="{} line in {}".format(str(error_line), error_file),
                raised=str(error.__class__.__name__),
                msg=str(error.ex),
            )

        email = user["email"].split("@") if user and user["email"] else None
        user_log = dict(
            client=request.state.ip,
            user=user["login_id"] if user and user["login_id"] else None,
            email=("**" + email[0][2:-1] + "*@" + email[1] if user and user["email"] else None),
        )

        log_dict = dict(
            url=(request.url.hostname + request.url.path if request.url.hostname else request.url.path),
            method=str(request.method),
            statusCode=status_code,
            errorDetail=error_log,
            client=user_log,
            processedTime=str(round(t * 1000, 5)) + "ms",
            datetimeUTC=datetime.utcnow().strftime(time_format),
            datetimeKST=(datetime.utcnow() + timedelta(hours=9)).strftime(time_format),
        )
        if error and error.status_code >= 500:
            logger.error(json.dumps(log_dict))
        else:
            logger.info(json.dumps(log_dict))
