from pydantic import BaseModel, ConfigDict


class LocationCreate(BaseModel):
    city_name: str


class LocationResponse(BaseModel):
    id: int
    city_name: str

    model_config = ConfigDict(orm_mode=True)