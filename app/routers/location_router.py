"""
Location Router
In this file, we define the endpoints for the locations. We have three endpoints:
- create_location_endpoint: This endpoint is used to create a new location.
- get_all_locations_endpoint: This endpoint is used to get all locations.
- get_location_by_id_endpoint: This endpoint is used to get a location by its id.
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.data.schemas.locations import LocationCreate, LocationResponse
from app.services.location_service import (
    create_location,
    get_all_locations,
    get_location_by_id,
)
locations_router = APIRouter(tags=["Locations"], prefix="/locations")

@locations_router.post("/", response_model=LocationResponse)
def create_location_endpoint(location_data: LocationCreate, db: Session = Depends(get_db)):
    """
    Create a new location
    Accepts a LocationCreate object as a request body and returns a LocationResponse object.
    """
    location = create_location(db, location_data)
    return location

@locations_router.get("/", response_model=List[LocationResponse])
def get_all_locations_endpoint(db: Session = Depends(get_db)):
    """
    Get all locations
    Returns a list of LocationResponse objects.
    """
    locations = get_all_locations(db)
    return locations

@locations_router.get("/{location_id}", response_model=LocationResponse)
def get_location_by_id_endpoint(location_id: int, db: Session = Depends(get_db)):
    """
    Get a location by its id
    Accepts a location id as a path parameter and returns a LocationResponse object.
    """
    location = get_location_by_id(db, location_id)
    return location
