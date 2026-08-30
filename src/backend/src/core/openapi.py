"""OpenAPI configuration for the custom Bearer JWT dependency."""

from typing import cast

from fastapi import FastAPI, routing
from fastapi.dependencies.models import Dependant
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from src.middleware.auth_middleware import require_authentication


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
        self.add_dependency_security(schema)
        self.openapi_schema = schema
        return schema

    def add_dependency_security(self, schema: dict[str, object]) -> None:
        """Add Bearer security to operations using auth or role dependencies."""
        raw_paths = schema.get("paths")
        if not isinstance(raw_paths, dict):
            return
        paths = cast(dict[str, object], raw_paths)
        for route_context in routing.iter_route_contexts(self.routes):
            original_route = route_context.original_route
            if not isinstance(original_route, APIRoute) or not self.uses_bearer_auth(
                original_route.dependant
            ):
                continue
            path_format = route_context.path_format
            methods = route_context.methods
            if path_format is None or methods is None:
                continue
            raw_path_item = paths.get(path_format)
            if not isinstance(raw_path_item, dict):
                continue
            path_item = cast(dict[str, object], raw_path_item)
            for method in methods:
                raw_operation = path_item.get(method.lower())
                if not isinstance(raw_operation, dict):
                    continue
                operation = cast(dict[str, object], raw_operation)
                operation["security"] = [{"BearerAuth": []}]

    @staticmethod
    def uses_bearer_auth(dependant: Dependant) -> bool:
        """Recursively detect authentication in a route dependency tree."""
        if dependant.call is require_authentication:
            return True
        return any(
            BearerOpenAPIFastAPI.uses_bearer_auth(child)
            for child in dependant.dependencies
        )
