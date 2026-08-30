from fastapi import Depends

from src.service.email_service import EmailService
from src.module.health.health_service import HealthService

def get_email_service() -> EmailService: 
    return EmailService() 
def get_health_service(
        email_service = Depends(get_email_service)
) -> HealthService:
    return HealthService(
        email_service = email_service
    )
