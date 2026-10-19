"""Static checks for the Alembic migration chain."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_ROOT = Path(__file__).resolve().parents[2]
FRESHCHECK_ASSESSMENT_REVISION = "98d6d2fdff50"
AI_CATALOG_REVISION = "e2b4f68a10cd"


def test_freshcheck_assessment_revision_is_the_only_alembic_head() -> None:
    """CI rejects divergent migrations before any database is contacted."""
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))

    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()

    assert heads == [AI_CATALOG_REVISION]
    ai_rev = script.get_revision(AI_CATALOG_REVISION)
    assert ai_rev is not None
    assert ai_rev.down_revision == FRESHCHECK_ASSESSMENT_REVISION
