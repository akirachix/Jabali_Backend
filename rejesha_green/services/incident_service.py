import uuid

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from rejesha_green.schemas.incidents import (
    IncidentReportCreate,
    IncidentReportUpdate,
)

from rejesha_green.repositories.incident_repository import (
    incident_report_repository,
)


def get_incident_report(
    db: Session,
    incident_id: uuid.UUID,
):
    incident = incident_report_repository.get(
        db,
        incident_id,
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident report not found",
        )

    return incident


def list_incident_report(db: Session):
    return incident_report_repository.get_all(db)


def create_incident_report(
    db: Session,
    data: IncidentReportCreate,
):
    return incident_report_repository.create_incident_report(
        db,
        data.model_dump(),
    )


def update_incident_report(
    db: Session,
    incident_id: uuid.UUID,
    data: IncidentReportUpdate,
):
    incident = get_incident_report(
        db,
        incident_id,
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    return incident_report_repository.update(
        db,
        incident,
        update_data,
    )


def delete_incident_report(
    db: Session,
    incident_id: uuid.UUID,
):
    incident = get_incident_report(
        db,
        incident_id,
    )

    return incident_report_repository.delete(
        db,
        incident,
    )