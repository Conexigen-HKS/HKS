from fastapi import FastAPI
import uvicorn

from HKS.routers.user_router import users_router

app = FastAPI()

app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)