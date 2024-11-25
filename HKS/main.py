from fastapi import FastAPI

from app.routers.job_application_router import job_app_router
from app.routers.locations_router import locations_router
from app.routers.skills import skills_router
from app.routers.user_router import users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(job_app_router)
app.include_router(skills_router)
app.include_router(locations_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)