"""
Admin service module.
In this file, we define the service functions for the admin service.
We have the following functions:
- approve_user: This function is used to approve a user.
- waiting_approvals: This function is used to get all waiting approvals.
- delete_user: This function is used to delete a user.
- approve_requirement: This function is used to approve a requirement.
- block_or_unblock_user: This function is used to block or unblock a user.
"""
from uuid import UUID


from sqlalchemy.orm import Session, joinedload

from fastapi import HTTPException, status

from app.data.models import Companies, Professional, User
from app.data.schemas.company import CompanyOut
from app.data.schemas.professional import ProfessionalOut
from app.data.schemas.users import WaitingApproval


def approve_user(id: str, entity_type: str, db: Session):
    """
    Approve a user
    :param id: The ID of the user to approve
    :param entity_type: The type of entity to approve
    :param db: The database session
    :return: The approved entity
    """
    if entity_type == "professional":
        entity = db.query(Professional).filter(Professional.id == id).first()
    elif entity_type == "company":
        entity = db.query(Companies).filter(Companies.id == id).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entity type '{entity_type}' is not valid",
        )

    if entity:
        entity.is_approved = True
        db.commit()
        db.refresh(entity)
        return entity

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity_type.capitalize()} with ID {id} not found",
    )


def waiting_approvals(db: Session) -> WaitingApproval:
    """
    Get all waiting approvals
    :param db: The database session
    :return: A WaitingApproval object
    """
    waiting_professionals = (
        db.query(Professional, User.username)
        .join(User, Professional.user_id == User.id)
        .options(joinedload(Professional.location))
        .filter(Professional.is_approved.is_(False))
        .all()
    )

    waiting_companies = (
        db.query(Companies, User.username)
        .join(User, Companies.user_id == User.id)
        .options(joinedload(Companies.location))
        .filter(Companies.is_approved.is_(False))
        .all()
    )

    professionals_out = [
        ProfessionalOut(
            id=professional.id,
            first_name=professional.first_name,
            last_name=professional.last_name,
            location_name=professional.location.city_name
            if professional.location
            else "N/A",
            phone=professional.phone,
            email=professional.email,
            website=professional.website,
            is_approved=professional.is_approved,
            username=username,
        )
        for professional, username in waiting_professionals
    ]

    company_out = [
        CompanyOut(
            id=company.id,
            name=company.name,
            description=company.description,
            location=company.location.city_name if company.location else "N/A",
            phone=company.phone,
            email=company.email,
            website=company.website,
            is_approved=company.is_approved,
            username=username,
        )
        for company, username in waiting_companies
    ]

    return WaitingApproval(professionals=professionals_out, companies=company_out)


def delete_user(id: str, db: Session):
    """
    Delete a user
    :param id: The ID of the user to delete
    :param db: The database session
    :return: A message indicating the user was deleted successfully
    """
    try:
        user_id = UUID(id)
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {id} not found")

        db.delete(user)
        try:
            db.commit()
            return {"message": "User and related data deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while deleting user: {str(e)}"
            ) from e
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid UUID format") from exc


def approve_requirement(id: str, db: Session, current_user: User):
    """
    Approve a requirement
    :param id: The ID of the requirement to approve
    :param db: The database session
    :param current_user: The current user
    :return: The approved requirement
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not authorized.")


def block_or_unblock_user(user_id: str, db: Session, current_user: User):
    """
    Block or unblock a user
    :param user_id: The ID of the user to block/unblock
    :param db: The database session
    :param current_user: The current user
    :return: The blocked/unblocked user
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not authorized.")

    try:
        user_id = UUID(user_id)
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        if user.role == 'professional':
            professional = db.query(Professional).options(
                joinedload(Professional.location),
                joinedload(Professional.user)
            ).filter(Professional.user_id == user_id).first()

            if professional:
                professional.status = 'blocked' if professional.status == 'active' else 'active'
                db.commit()
                db.refresh(professional)
                return professional

        elif user.role == 'company':
            company = db.query(Companies).options(
                joinedload(Companies.location),
                joinedload(Companies.user)
            ).filter(Companies.user_id == user_id).first()

            if company:
                company.status = 'blocked' if company.status == 'active' else 'active'
                db.commit()
                db.refresh(company)
                return company

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format"
        ) from exc
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error while blocking/unblocking user: {str(e)}"
        ) from e
