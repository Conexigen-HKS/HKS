from fastapi import FastAPI

import uvicorn
from routers.company_router import company_router

app = FastAPI()

app.include_router(company_router)

if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
