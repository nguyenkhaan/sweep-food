from typing import Never

from fastapi import HTTPException, status
from src.base.constant.template_file_name import _TEMPLATE_FILENAMES
from src.service.email_service import EmailService
from src.module.health.health_dto import LivenessResponseDTO


class HealthService:
    def __init__(self , email_service : EmailService): 
        self.email_service = email_service
    def get_liveness(self) -> LivenessResponseDTO: 
        return LivenessResponseDTO(
            message = "Build with Cloudian 💙 Cloud"
        )

    def raise_forced_error(self) -> Never:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Forced health error.",
        )

    def get_text(self) -> str:

        return "Build with Cloudian Love Cloud"
    async def send_email(self): 
        await self.email_service.send_email(
            "Testing email", 
            {
                "recipient": "Cloudian@gmail.com", 
                "name": "Cloudian"
            }, 
            _TEMPLATE_FILENAMES['BASE_HTML']
        )
