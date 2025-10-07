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
# Patch dbx MlflowStorageConfigurationManager experiment validation
# ---------------------------------------------------------------------------
try:  # pragma: no cover - defensive import
    from dbx.api.storage.mlflow_based import MlflowStorageConfigurationManager  # type: ignore
    from mlflow.tracking import MlflowClient as _PatchClient  # reuse

    _orig_setup_experiment = MlflowStorageConfigurationManager._setup_experiment  # type: ignore[attr-defined]

    def _patched_setup_experiment(cls, env):  # type: ignore[override]
        """Wrap original _setup_experiment.

        If it raises the artifact location mismatch exception, adjust
        env.properties.artifact_location to the actual experiment artifact
        location and retry once. This avoids hard failure in workspaces that
        reject the original root artifact path.
        """
        try:
            return _orig_setup_experiment(cls, env)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            mismatch_phrase = "Required location of experiment"
            if mismatch_phrase not in msg:
                raise
            try:
                exp_name = getattr(env.properties, "workspace_directory", None) or getattr(env, "workspace_directory", None)
                client = _PatchClient()
                exp = client.get_experiment_by_name(exp_name) if exp_name else None
                if exp and hasattr(env, "properties"):
                    print(
                        f"[sitecustomize] Adjusting env.properties.artifact_location from "
                        f"'{getattr(env.properties, 'artifact_location', None)}' to '{exp.artifact_location}'"
                    )
                    env.properties.artifact_location = exp.artifact_location  # type: ignore[attr-defined]
                    # Retry once after adjustment
                    return _orig_setup_experiment(cls, env)
            except Exception as inner:  # noqa: BLE001
                print(f"[sitecustomize] Failed to auto-adjust artifact location: {inner}")
            # If we reach here, re-raise original
            raise

    MlflowStorageConfigurationManager._setup_experiment = classmethod(_patched_setup_experiment)  # type: ignore
except Exception as _patch_exc:  # pragma: no cover
    print(f"[sitecustomize] Skipping dbx _setup_experiment patch: {_patch_exc}")
