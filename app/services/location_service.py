from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.data.models import Location
from app.data.schemas.location import LocationCreate


def create_location(db: Session, location_data: LocationCreate):
    existing_location = db.query(Location).filter(Location.city_name == location_data.city_name).first()
    if existing_location:
        raise HTTPException(status_code=400, detail="Location already exists")

    new_location = Location(city_name=location_data.city_name)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


def get_all_locations(db: Session):
    return db.query(Location).all()


def get_location_by_id(db: Session, location_id: UUID):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location