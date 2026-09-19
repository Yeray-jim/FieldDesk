"""Packaging entry point.

`flet build` and `flet run` look for a module with this name at the project
root; it simply delegates to the application bootstrap.
"""

from __future__ import annotations

from app.main import run

if __name__ == "__main__":
    run()
