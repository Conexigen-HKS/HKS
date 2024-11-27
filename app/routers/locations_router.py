from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from HKS.data.database import get_db
from HKS.data.schemas.locations import LocationCreate, LocationResponse
from app.services.locations_services import create_location, get_all_locations, get_location_by_id

locations_router = APIRouter(tags=["Locations"], prefix="/locations")

@locations_router.post("/", response_model=LocationResponse)
def create_location_endpoint(location_data: LocationCreate, db: Session = Depends(get_db)):
    location = create_location(db, location_data)
    return location

@locations_router.get("/", response_model=List[LocationResponse])
def get_all_locations_endpoint(db: Session = Depends(get_db)):
    locations = get_all_locations(db)
    return locations

@locations_router.get("/{location_id}", response_model=LocationResponse)
def get_location_by_id_endpoint(location_id: UUID, db: Session = Depends(get_db)):
    location = get_location_by_id(db, location_id)
    return location