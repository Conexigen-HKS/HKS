"""
This module contains custom response classes that
can be used to return responses from FastAPI endpoints.
"""

from typing import Any
from fastapi import Response, HTTPException, status


class Complete(Response):
    def __init__(self):
        super().__init__(status_code=200, media_type="application/json")


class Accepted(Response):
    def __init__(self, content: Any = None):
        super().__init__(
            status_code=202, content=content, media_type="application/json"
        )


class NoContent(Response):
    def __init__(self):
        super().__init__(status_code=204, media_type="application/json")


class BadRequest(HTTPException):
    def __init__(self, content: Any = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail=content)


class Unauthorized(HTTPException):
    def __init__(self, content: Any = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail=content)


class Forbidden(HTTPException):
    def __init__(self, content: Any = None):
        super().__init__(status.HTTP_403_FORBIDDEN, detail=content)


class NotFound(HTTPException):
    def __init__(self, content: Any = None):
        super().__init__(status.HTTP_404_NOT_FOUND, detail=content)


class InternalServerError(HTTPException):
    def __init__(self, content: Any = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=content)
