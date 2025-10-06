"""Monkeypatch MLflow experiment creation to avoid disallowed DBFS root paths.

dbx currently attempts to create an experiment with an artifact_location like
`dbfs:/dbx/<project-name>` which is blocked in workspaces that disallow DBFS
root access. This patch intercepts MlflowClient.create_experiment and drops
the artifact_location argument when it points to a disallowed prefix so that
the Databricks backend assigns a safe default path (usually under
`dbfs:/databricks/mlflow-tracking/`).

Loaded automatically because this file is named `sitecustomize.py` and its
directory is appended to PYTHONPATH in the GitHub Actions workflow.
"""
from __future__ import annotations

from typing import Any, Iterable

try:
    from mlflow.tracking.client import MlflowClient  # type: ignore
except Exception:  # pragma: no cover
    MlflowClient = None  # type: ignore

DISALLOWED_PREFIXES = ("dbfs:/dbx/",)

if MlflowClient is not None:  # pragma: no branch
    _orig_create = MlflowClient.create_experiment

    def _safe_create(self, name: str, artifact_location: str | None = None, tags: Iterable[Any] | None = None):  # type: ignore[override]
        if artifact_location and artifact_location.startswith(DISALLOWED_PREFIXES):
            # Drop the disallowed artifact root so backend assigns default allowed location
            print(
                f"[sitecustomize] Overriding disallowed artifact_location '{artifact_location}' for experiment '{name}'"
            )
            artifact_location = None
        return _orig_create(self, name, artifact_location=artifact_location, tags=tags)

    MlflowClient.create_experiment = _safe_create  # type: ignore
