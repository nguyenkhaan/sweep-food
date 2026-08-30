import json

import httpx

from src.core.setting import SMS_DELIVERY_TIMEOUT_SECONDS, WIREMOCK_URL
from src.service.otp_delivery_service import (
    OTPDeliveryMalformedResponseError,
    OTPDeliveryRejectedError,
    OTPDeliveryRequest,
    OTPDeliveryRequestError,
    OTPDeliveryService,
    OTPDeliveryTimeoutError,
)

"""
Thong thuong viec gui OTP se ton tai 2 luong: 
1. Provider tao OTP 
- App chi can yeu cau gui OTP den so nay, provider se thuc hien sinh OTP, sau do gui den client lan app 
- Bi phu thuoc vao ben provider 
2. Backend tu tao OTP  
- Backend se tu tao OTP, sau do provider chi nhan noi dung va tien hanh chuyen tiep SMS/email den noi phu hop 


"""
class WireMockSMSService(OTPDeliveryService):
    def __init__(
        self,
        base_url: str = WIREMOCK_URL,
        timeout_seconds: int = SMS_DELIVERY_TIMEOUT_SECONDS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Configure WireMock URL, timeout, and optional test transport."""
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def send_otp(self, request: OTPDeliveryRequest) -> str:
        """Send an OTP through WireMock and return its delivery reference."""
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    "/mock/sms",
                    json={
                        "destination": request.destination,
                        "template_id": request.template_id,
                        "otp": request.otp,
                        "expires_in_seconds": request.expires_in_seconds,
                        "correlation_id": request.correlation_id,
                    },
                )
        except httpx.TimeoutException as error:
            raise OTPDeliveryTimeoutError() from error
        except httpx.RequestError as error:
            raise OTPDeliveryRequestError() from error

        if response.status_code >= 400:
            raise OTPDeliveryRejectedError()
        return self._parse_delivery_reference(response)

    @staticmethod
    def _parse_delivery_reference(response: httpx.Response) -> str:
        try:
            body: object = response.json()
        except json.JSONDecodeError as error:
            raise OTPDeliveryMalformedResponseError() from error
        if not isinstance(body, dict):
            raise OTPDeliveryMalformedResponseError()

        status = body.get("status")
        delivery_reference = body.get("delivery_reference")
        if status != "accepted" or not isinstance(delivery_reference, str):
            raise OTPDeliveryMalformedResponseError()
        return delivery_reference
