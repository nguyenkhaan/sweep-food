"""Static checks for the FreshCheck Alembic migration chain."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_ROOT = Path(__file__).resolve().parents[2]
FRESHCHECK_ASSESSMENT_REVISION = "98d6d2fdff50"


def test_freshcheck_assessment_revision_is_the_only_alembic_head() -> None:
    """CI rejects divergent migrations before any database is contacted."""
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))

    heads = ScriptDirectory.from_config(config).get_heads()

    assert heads == [FRESHCHECK_ASSESSMENT_REVISION]
