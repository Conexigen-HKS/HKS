from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers.company_ad_router import company_ad_router
from app.routers.company_router import company_router
from app.routers.user_router import users_router
from app.routers.admin_router import admin_router
from app.routers.message_router import messages_router
from app.routers.match_router import match_router
import uvicorn


app = FastAPI()
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(messages_router)
app.include_router(match_router)
app.include_router(company_router)
app.include_router(company_ad_router)
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=400,
#         content={"message": "Validation error: " + str(exc)}
#     )
#
# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request: Request, exc: StarletteHTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": exc.detail}
#     )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
