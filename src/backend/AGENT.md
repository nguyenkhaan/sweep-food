# Python — AGENTS Protocol

## Python

### Minimum Required Linters

- **ruff** — fast all-in-one linter and formatter (replaces flake8, isort, pyflakes, etc.)
- **mypy** — static type checker with `--strict` flag
- **pylint** — deep static analysis (yes, in addition to ruff — they catch different things)

All three must pass with **zero** warnings, **zero** errors, **zero** suppressions.

Install if missing:
```bash
pip install ruff mypy pylint
```

Run:
```bash
ruff check . && ruff format --check . && mypy --strict . && pylint **/*.py
```

### Type Hints Are Mandatory

Every function signature must have complete type annotations. No exceptions.
`Any` is not a type hint — it's a surrender. If you reach for `Any`, you
don't understand the data flow well enough yet.

```python
# GOOD
def parse_response(data: bytes, encoding: str = "utf-8") -> dict[str, list[int]]:
    ...

# BAD
def parse_response(data, encoding="utf-8"):
    ...

# TERRIBLE
def parse_response(data: Any) -> Any:
    ...
```

### No Bare Excepts, No Broad Excepts

```python
# GOOD: Catch specific exceptions, handle them meaningfully
try:
    config = json.loads(raw_data)
except json.JSONDecodeError as exc:
    raise ConfigError(
        f"Failed to parse config from {source}: {exc}"
    ) from exc

# BAD: Catches everything including KeyboardInterrupt and SystemExit
try:
    config = json.loads(raw_data)
except Exception:
    config = {}  # "sensible default" that masks the real problem

# FORBIDDEN: The silent killer
try:
    config = json.loads(raw_data)
except:
    pass
```

### String Formatting

Use f-strings. Not `%` formatting. Not `.format()`. f-strings are faster,
more readable, and harder to get wrong.

```python
# GOOD
msg = f"Connection to {host}:{port} failed after {retries} retries"

# BAD
msg = "Connection to %s:%d failed after %d retries" % (host, port, retries)

# ALSO BAD
msg = "Connection to {}:{} failed after {} retries".format(host, port, retries)
```

### Imports

Imports are at the top of the file. Always. No inline imports unless there
is a genuine circular dependency issue, and even then, restructure the code
to avoid it if at all possible.

```python
# GOOD
from pathlib import Path
from collections.abc import Sequence

def process(paths: Sequence[Path]) -> None:
    ...

# BAD
def process(paths):
    from pathlib import Path  # why is this here?
    ...
```

### Pathlib Over os.path

```python
# GOOD
from pathlib import Path

config_dir = Path.home() / ".config" / "myapp"
config_dir.mkdir(parents=True, exist_ok=True)
config_file = config_dir / "settings.json"
text = config_file.read_text(encoding="utf-8")

# BAD
import os

config_dir = os.path.join(os.path.expanduser("~"), ".config", "myapp")
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, "settings.json")
with open(config_file, "r") as f:
    text = f.read()
```

### Context Managers for Resources

If it opens, it closes. Period.

```python
# GOOD
with open(path, "r", encoding="utf-8") as fh:
    data = json.load(fh)

# BAD: file handle leak if json.load raises
fh = open(path, "r")
data = json.load(fh)
fh.close()
```

### Never Use Mutable Default Arguments

```python
# GOOD
def append_item(item: str, target: list[str] | None = None) -> list[str]:
    if target is None:
        target = []
    target.append(item)
    return target

# BAD: The list is shared across ALL calls
def append_item(item: str, target: list[str] = []) -> list[str]:
    target.append(item)
    return target
```

This is not a style preference. The "bad" version is a bug. The default
list is created once at function definition time and shared across all
calls. This is one of the most common Python traps and agents fall into it
regularly.

