from fastapi import Response
from typing import Any


class Complete(Response):
    def __init__(self):
        super().__init__(status_code=200, media_type="application/json")


class Accepted(Response):
    def __init__(self, content: Any = None):
        super().__init__(status_code=202, content=content, media_type="application/json")


class NoContent(Response):
    def __init__(self):
        super().__init__(status_code=204, media_type="application/json")


class BadRequest(Response):
    def __init__(self, content: Any = None):
        super().__init__(status_code=400, content=content, media_type="application/json")


class Unauthorized(Response):
    def __init__(self, content: Any = None):
        super().__init__(status_code=401, content=content, media_type="application/json")


class Forbidden(Response):
    def __init__(self, content: Any = None):
        super().__init__(status_code=403, content=content, media_type="application/json")


class NotFound(Response):
    def __init__(self, content: Any = None):
        super().__init__(status_code=404, content=content, media_type="application/json")


class InternalServerError(Response):
    def __init__(self, content: Any = None):
        super().__init__(status_code=500, content=content, media_type="application/json")

