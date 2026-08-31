"""Local Uvicorn entry point for the Sweep Food backend."""

import uvicorn


def main() -> None:
    """Run the development server with automatic reload."""
    uvicorn.run("src.app:app", host="0.0.0.0", port=4000, reload=True)


if __name__ == "__main__":
    main()
