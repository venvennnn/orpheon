"""Load Orpheon YAML configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml

from .paths import PROJECTS_CONFIG, SITE_CONFIG


@dataclass(frozen=True)
class ProjectConfig:
    repository: str
    slug: str
    enabled: bool = True

    @property
    def owner(self) -> str:
        return self.repository.split("/", 1)[0]

    @property
    def name(self) -> str:
        return self.repository.split("/", 1)[1]


def load_yaml(path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_site_config() -> dict[str, Any]:
    return load_yaml(SITE_CONFIG).get("site", {})


def load_projects(path=PROJECTS_CONFIG) -> list[ProjectConfig]:
    raw = load_yaml(path)
    projects: list[ProjectConfig] = []
    for item in raw.get("projects", []) or []:
        if not item.get("repository") or not item.get("slug"):
            continue
        projects.append(
            ProjectConfig(
                repository=str(item["repository"]),
                slug=str(item["slug"]),
                enabled=bool(item.get("enabled", True)),
            )
        )
    return projects


def enabled_projects() -> list[ProjectConfig]:
    return [project for project in load_projects() if project.enabled]
