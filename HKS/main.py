from HKS.data.databaseScript.models import UsersBase
from HKS.data.databaseScript.database import Session
from fastapi import FastAPI
from HKS.routers.user_router import users_router
import uvicorn


app = FastAPI()

app.include_router(users_router)

if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)