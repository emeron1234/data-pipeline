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
# Patch dbx MlflowStorageConfigurationManager experiment validation (robust *args)
# ---------------------------------------------------------------------------
try:  # pragma: no cover - defensive import
    from dbx.api.storage.mlflow_based import MlflowStorageConfigurationManager  # type: ignore
    from mlflow.tracking import MlflowClient as _PatchClient  # reuse

    _orig_setup_experiment_any = MlflowStorageConfigurationManager._setup_experiment  # could be bound or func

    def _patched_setup_experiment_any(*args, **kwargs):  # type: ignore
        """Universal wrapper for _setup_experiment supporting any bound form.

        On artifact location mismatch, synchronize env.properties.artifact_location
        with the actual experiment artifact path and retry once. If retry still
        fails, emit a warning and return the experiment object so deployment can proceed.
        """
        try:
            return _orig_setup_experiment_any(*args, **kwargs)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "Required location of experiment" not in msg:
                raise
            # Extract env (last positional arg or 'env' kwarg)
            env = kwargs.get("env") or (args[-1] if args else None)
            try:
                exp_name = None
                if env is not None:
                    props = getattr(env, "properties", None)
                    exp_name = (
                        getattr(props, "workspace_directory", None)
                        or getattr(env, "workspace_directory", None)
                    )
                client = _PatchClient()
                exp = client.get_experiment_by_name(exp_name) if exp_name else None
                if exp and env and getattr(env, "properties", None):
                    current = getattr(env.properties, "artifact_location", None)
                    if current != exp.artifact_location:
                        print(
                            f"[sitecustomize] Harmonizing artifact_location: '{current}' -> '{exp.artifact_location}'"
                        )
                        env.properties.artifact_location = exp.artifact_location  # type: ignore[attr-defined]
                    # Retry once
                    try:
                        return _orig_setup_experiment_any(*args, **kwargs)
                    except Exception as e2:  # noqa: BLE001
                        print(
                            f"[sitecustomize] Retry after harmonization still failed: {e2}. Proceeding with experiment object."  # noqa: E501
                        )
                        return exp
                print(
                    "[sitecustomize] Artifact mismatch detected but experiment not resolvable; continuing (may fail later)."
                )
                return None
            except Exception as inner:  # noqa: BLE001
                print(f"[sitecustomize] Failed mismatch mitigation: {inner}; re-raising original error")
                raise e

    # Preserve descriptor type (classmethod vs function) if applicable
    if isinstance(MlflowStorageConfigurationManager.__dict__.get("_setup_experiment"), classmethod):
        MlflowStorageConfigurationManager._setup_experiment = classmethod(_patched_setup_experiment_any)  # type: ignore
    else:
        MlflowStorageConfigurationManager._setup_experiment = _patched_setup_experiment_any  # type: ignore
except Exception as _patch_exc:  # pragma: no cover
    print(f"[sitecustomize] Skipping resilient dbx _setup_experiment patch: {_patch_exc}")
