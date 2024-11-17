
from fastapi import FastAPI

import uvicorn


app = FastAPI()

# company.include_router(users_router)

if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)

