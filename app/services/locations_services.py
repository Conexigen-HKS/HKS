from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.data.models import Locations
from app.data.schemas.locations import LocationCreate


def create_location(db: Session, location_data: LocationCreate):
    # Check if location already exists
    existing_location = db.query(Locations).filter(Locations.name == location_data.name).first()
    if existing_location:
        raise HTTPException(status_code=400, detail="Location already exists")

    # Create new location
    new_location = Locations(name=location_data.name)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


def get_all_locations(db: Session):
    # Retrieve all locations
    return db.query(Locations).all()


def get_location_by_id(db: Session, location_id: UUID):
    # Retrieve a location by ID
    location = db.query(Locations).filter(Locations.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location
