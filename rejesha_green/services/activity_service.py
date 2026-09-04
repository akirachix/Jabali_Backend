from uuid import UUID
from sqlalchemy.orm import Session
from rejesha_green.models.activity import Activity
from rejesha_green.repositories.activity_repository import ActivityRepository
from rejesha_green.schemas.activities import (
    ActivityCreate,
    ActivityUpdate,
)
from rejesha_green.services.sms_service import SMSService


class ActivityService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ActivityRepository(db)
        self.sms_service = SMSService()

    def _get_recipient_phone_numbers(self) -> list[str]:
        from rejesha_green.models.user import User
        
        users = self.db.query(User).filter(User.is_active == True).all()
        phone_numbers = [u.phone for u in users if u.phone]
        return list(set(phone_numbers))

    def create_activity(
        self,
        activity_data: ActivityCreate,
    ) -> Activity:

        activity = Activity(
            created_by=activity_data.created_by,
            zone_id=activity_data.zone_id,
            activity_name=activity_data.activity_name,
            scheduled_date=activity_data.scheduled_date,
            description=activity_data.description,
            user_group=activity_data.user_group,
            expected_attendees=activity_data.expected_attendees,
            actual_attendees=activity_data.actual_attendees,
        )

        created_activity = self.repository.create(activity)

        message = (
            f"REJESHA GREEN\n"
            f"You are invited to a community activity.\n"
            f"Activity: {created_activity.activity_name}\n"
            f"Date: {created_activity.scheduled_date}\n"
            f"Group: {created_activity.user_group.value if created_activity.user_group else 'All Members'}\n"
            f"Zone: {created_activity.zone_id}\n"
            f"Details: {created_activity.description or 'Please contact your coordinator for details.'}\n"
            f"Kindly make the necessary arrangements to participate.\n"
            f"Thank you.\n"
            f"- Rejesha Green "
        )
        
        phone_numbers = self._get_recipient_phone_numbers()

        if phone_numbers:
            sms_results = self.sms_service.send_bulk_sms(
                phone_numbers=phone_numbers,
                message=message,
            )
            print("SMS RESULTS:", sms_results)

        return created_activity

    def get_activity(
        self,
        activity_id: str,
    ):
        return self.repository.get_by_id(activity_id)

    def get_activities(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        return self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    def get_activities_by_zone(
        self,
        zone_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ):
        return self.repository.get_by_zone(
            zone_id=zone_id,
            skip=skip,
            limit=limit,
        )

    def get_upcoming_activities(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        return self.repository.get_upcoming(
            skip=skip,
            limit=limit,
        )

    def update_activity(
        self,
        activity_id: str,
        activity_data: ActivityUpdate,
    ):
        activity = self.repository.get_by_id(activity_id)

        if activity is None:
            return None

        update_data = activity_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(activity, field, value)

        updated_activity = self.repository.update(activity)

        message = (
            f"REJESHA GREEN UPDATE\n"
            f"An activity has been updated.\n"
            f"Activity: {updated_activity.activity_name}\n"
            f"Date: {updated_activity.scheduled_date}\n"
            f"Group: {updated_activity.user_group.value if updated_activity.user_group else 'All Members'}\n"
            f"Zone: {updated_activity.zone_id}\n"
            f"Details: {updated_activity.description or 'Please contact your coordinator for details.'}\n"
            f"Please take note of the changes.\n"
            f"Thank you.\n"
            f"- Rejesha Green"
        )

        phone_numbers = self._get_recipient_phone_numbers()

        if phone_numbers:
            sms_results = self.sms_service.send_bulk_sms(
                phone_numbers=phone_numbers,
                message=message,
            )
            print("UPDATE SMS RESULTS:", sms_results)

        return updated_activity

    def delete_activity(
        self,
        activity_id: str,
    ):
        activity = self.repository.get_by_id(activity_id)

        if activity is None:
            return None

        message = (
            f"REJESHA GREEN CANCELLATION\n"
            f"An activity has been cancelled.\n"
            f"Activity: {activity.activity_name}\n"
            f"Scheduled Date: {activity.scheduled_date}\n"
            f"This activity will no longer take place. Please disregard previous invitations.\n"
            f"Thank you.\n"
            f"- Rejesha Green"
        )

        phone_numbers = self._get_recipient_phone_numbers()

        if phone_numbers:
            sms_results = self.sms_service.send_bulk_sms(
                phone_numbers=phone_numbers,
                message=message,
            )
            print("DELETE SMS RESULTS:", sms_results)

        self.repository.delete(activity)

        return activity
