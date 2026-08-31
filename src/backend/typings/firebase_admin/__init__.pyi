"""Minimal Firebase Admin types used by Sweep Food."""

from collections.abc import Mapping

from firebase_admin.credentials import Certificate

class App: ...

def get_app(name: str = "[DEFAULT]") -> App: ...
def initialize_app(
    credential: Certificate,
    options: Mapping[str, object] | None = None,
    name: str = "[DEFAULT]",
) -> App: ...
