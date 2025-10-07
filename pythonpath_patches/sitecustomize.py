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

# ---------------------------------------------------------------------------
# Patch dbx MlflowStorageConfigurationManager experiment validation (minimal no-op)
# ---------------------------------------------------------------------------
try:  # pragma: no cover - defensive import
    from dbx.api.storage.mlflow_based import MlflowStorageConfigurationManager  # type: ignore
    from mlflow.tracking import MlflowClient as _PatchClient  # reuse

    def _noop_setup_experiment(*args, **kwargs):  # type: ignore
        """No-op replacement for dbx _setup_experiment.

        Goal: bypass artifact location enforcement that fails on Free/Serverless
        workspaces. Ensures experiment exists and returns quietly. Accepts any
        signature to avoid TypeError (instance vs classmethod invocation).
        """
        # Attempt to extract env to derive experiment name for creation
        env = kwargs.get("env") or (args[-1] if args else None)
        exp_name = None
        if env is not None:
            props = getattr(env, "properties", None)
            exp_name = (
                getattr(props, "workspace_directory", None)
                or getattr(env, "workspace_directory", None)
            )
        try:
            if exp_name:
                client = _PatchClient()
                exp = client.get_experiment_by_name(exp_name)
                if not exp:
                    print(f"[sitecustomize] Creating experiment '{exp_name}' via no-op setup patch")
                    client.create_experiment(exp_name)
                else:
                    print(f"[sitecustomize] Experiment '{exp_name}' already exists (no-op setup)")
        except Exception as inner:  # noqa: BLE001
            print(f"[sitecustomize] _noop_setup_experiment could not ensure experiment: {inner}")
        return None

    # Always install as classmethod to satisfy call sites expecting classmethod
    MlflowStorageConfigurationManager._setup_experiment = classmethod(_noop_setup_experiment)  # type: ignore
    print("[sitecustomize] Installed no-op _setup_experiment patch for dbx")
except Exception as _patch_exc:  # pragma: no cover
    print(f"[sitecustomize] Skipping no-op dbx _setup_experiment patch: {_patch_exc}")
