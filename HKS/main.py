from fastapi import FastAPI
from pydantic import ValidationError

from HKS.routers.job_application_router import job_app_router
from HKS.routers.professional import professional_router
from HKS.routers.skills import skills_router
from HKS.routers.user_router import users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(professional_router)
app.include_router(job_app_router)
app.include_router(skills_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)