from __future__ import annotations

from importlib import resources
from pathlib import Path


PACKAGE_NAME = "ai-collab-blackbox"


def package_root() -> Path:
    return Path(__file__).resolve().parent


def resources_root():
    return resources.files(__package__) / "resources"


def read_text(name: str) -> str:
    return (resources_root() / name).read_text(encoding="utf-8")


def iter_reference_names() -> list[str]:
    refs = resources_root() / "references"
    return sorted(item.name for item in refs.iterdir() if item.is_file())


def read_reference(name: str) -> str:
    return (resources_root() / "references" / name).read_text(encoding="utf-8")

