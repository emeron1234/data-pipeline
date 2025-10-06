"""Cleanup stale MLflow experiments that point to disallowed DBFS root artifact locations.

This script searches for experiments whose artifact_location starts with the
disallowed prefix 'dbfs:/dbx/' (e.g. 'dbfs:/dbx/data-pipeline') and deletes them
so that dbx can recreate them with the updated allowed FileStore location.

Safe-guards:
  * Only deletes experiments with artifact_location under dbfs:/dbx/
  * Skips experiments that are marked as deleted already
  * Prints a summary of actions

Requires DATABRICKS_HOST and DATABRICKS_TOKEN env vars (already present in workflow).
"""
from __future__ import annotations

import os
from typing import List

import mlflow
from mlflow.tracking import MlflowClient


DISALLOWED_PREFIXES = ["dbfs:/dbx/"]


def is_disallowed(artifact_location: str) -> bool:
    return any(artifact_location.startswith(p) for p in DISALLOWED_PREFIXES)


def main() -> None:
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    if not host or not token:
        print("Environment variables DATABRICKS_HOST and DATABRICKS_TOKEN are required.")
        return

    # mlflow will auto-detect databricks tracking via host/token env vars
    client = MlflowClient()

    to_delete: List[str] = []
    print("Scanning MLflow experiments for disallowed artifact locations ...")
    for exp in client.search_experiments():
        if exp.lifecycle_stage == "deleted":
            continue
        if exp.artifact_location and is_disallowed(exp.artifact_location):
            print(
                f" -> Marking experiment '{exp.name}' (id={exp.experiment_id}) for deletion: {exp.artifact_location}"
            )
            to_delete.append(exp.experiment_id)

    if not to_delete:
        print("No experiments with disallowed artifact locations found. Nothing to do.")
        return

    for exp_id in to_delete:
        try:
            client.delete_experiment(exp_id)
            print(f"Deleted experiment id={exp_id}")
        except Exception as e:  # noqa: BLE001
            print(f"Failed to delete experiment id={exp_id}: {e}")

    print("Cleanup complete.")


if __name__ == "__main__":
    main()
