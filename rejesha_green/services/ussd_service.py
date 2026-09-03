from sqlalchemy.orm import Session
from fastapi.responses import PlainTextResponse

from rejesha_green.services.permit_service import permit_service
from rejesha_green.models.incident import ActivityType
from rejesha_green.models.forest_zone import ForestZone
from rejesha_green.schemas.incidents import IncidentReportCreate
from rejesha_green.services.incident_service import (
    create_incident_report,
)


def handle_ussd(
    db: Session,
    session_id: str,
    phone_number: str,
    text: str,
):
    parts = text.split("*") if text else []

    # MAIN MENU
    if not parts:
        return PlainTextResponse(
            "CON Welcome to Rejesha Green\n"
            "1. Request Permit\n"
            "2. Report Incident"
        )

    # =========================
    # PERMIT FLOW
    # =========================
    if parts[0] == "1":

        response = permit_service.handle_ussd_request(
            db=db,
            session_id=session_id,
            phone_number=phone_number,
            text=text,
        )

        return PlainTextResponse(response)

    # =========================
    # INCIDENT FLOW
    # =========================
    if parts[0] == "2":

        incident_text = "*".join(parts[1:])

        return handle_incident(
            db=db,
            text=incident_text,
        )

    return PlainTextResponse(
        "END Invalid selection."
    )


def handle_incident(
    db: Session,
    text: str,
):
    parts = text.split("*") if text else []

    # INCIDENT TYPE MENU
    if len(parts) == 0:
        return PlainTextResponse(
            "CON Select Incident Type:\n"
            "1. Charcoal Burning\n"
            "2. Logging\n"
            "3. Poaching\n"
            "4. Others"
        )

    incident_types = {
        "1": ActivityType.Charcoal_Burning,
        "2": ActivityType.Logging,
        "3": ActivityType.Poaching,
        "4": ActivityType.Others,
    }

    # INCIDENT TYPE SELECTED
    if len(parts) == 1:

        selected_type = incident_types.get(parts[0])

        if selected_type is None:
            return PlainTextResponse(
                "END Invalid incident type."
            )

        zones = (
            db.query(ForestZone)
            .filter(
                ForestZone.is_available.is_(True)
            )
            .limit(5)
            .all()
        )

        if not zones:
            return PlainTextResponse(
                "END No forest zones available."
            )

        response = "CON Select Forest Zone:\n"

        for index, zone in enumerate(
            zones,
            start=1,
        ):
            response += (
                f"{index}. {zone.block_name}\n"
            )

        return PlainTextResponse(
            response.rstrip()
        )

    # INCIDENT TYPE + ZONE SELECTED
    if len(parts) == 2:

        selected_type = incident_types.get(parts[0])

        if selected_type is None:
            return PlainTextResponse(
                "END Invalid incident type."
            )

        zones = (
            db.query(ForestZone)
            .filter(
                ForestZone.is_available.is_(True)
            )
            .limit(5)
            .all()
        )

        try:
            zone_index = int(parts[1]) - 1
        except ValueError:
            return PlainTextResponse(
                "END Invalid zone selection."
            )

        if (
            zone_index < 0
            or zone_index >= len(zones)
        ):
            return PlainTextResponse(
                "END Invalid zone selection."
            )

        selected_zone = zones[zone_index]

        report_data = IncidentReportCreate(
            zone_id=selected_zone.zone_id,
            incident_type=selected_type,
        )

        create_incident_report(
            db,
            report_data,
        )

        return PlainTextResponse(
            "END Incident submitted successfully."
        )

    return PlainTextResponse(
        "END Invalid incident request."
    )