"""
This module contains the service functions for the Location model.
We have three functions:
- create_location: This function is used to create a new location.
- get_all_locations: This function is used to get all locations.
- get_location_by_id: This function is used to get a location by its ID.
"""

from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.data.models import Location, Skills
from app.data.schemas.locations import LocationCreate


def create_location(db: Session, location_data: LocationCreate):
    """
    Create a new location
    :param db: Database session
    :param location_data: Location data
    :return: New location
    """
    existing_location = (
        db.query(Location).filter(Location.city_name == location_data.city_name).first()
    )
    if existing_location:
        raise HTTPException(status_code=400, detail="Location already exists")

    new_location = Location(city_name=location_data.city_name)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


def get_all_locations(db: Session):
    """
    Get all locations
    :param db: Database session
    :return: List of locations
    """
    return db.query(Location).all()


def get_location_by_id(db: Session, location_id: UUID):
    """
    Get a location by its ID
    :param db: Database session
    :param location_id: Location ID
    :return: Location
    """
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

