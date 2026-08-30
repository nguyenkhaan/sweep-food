"""OpenAPI configuration for the custom Bearer JWT dependency."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


class BearerOpenAPIFastAPI(FastAPI):
    """FastAPI application that exposes the custom Bearer JWT in Swagger UI."""

    def openapi(self) -> dict[str, object]:
        """Build and cache an OpenAPI document with a Bearer security scheme."""
        if self.openapi_schema is not None:
            return self.openapi_schema

        schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.routes,
        )
        components = schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
        self.openapi_schema = schema
        return schema
