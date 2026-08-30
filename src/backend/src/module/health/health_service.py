from typing import Never

from fastapi import HTTPException, status

from src.module.health.health_dto import LivenessResponseDTO


class HealthService:

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
