# DBFS Root Access Issue - Troubleshooting Guide

## Problem
```
RestException: INVALID_PARAMETER_VALUE: The specified DBFS artifact location 
dbfs:/dbx/we-pipeline_dev_feature is a DBFS root location. DBFS root access is 
disabled in your workspace. Please use MLflow's default artifact location or 
specify an alternative artifact location, such as a location within 
'dbfs:/Volumes/...'.
```

## Root Cause
- DBFS root access is disabled in many Databricks workspaces (especially Free Edition)
- The original configuration uses `dbfs:/dbx/` which is a DBFS root location
- Modern Databricks workspaces restrict access to DBFS root for security reasons

## Solutions Implemented

### Solution 1: Use MLflow Default Artifact Location (Recommended)
✅ **Created**: `.dbx/project_free_edition.json` without `artifact_location`
- When `artifact_location` is omitted, MLflow uses its default location
- Default location is usually workspace-specific and allowed

### Solution 2: Use Allowed DBFS Paths
✅ **Updated**: `.dbx/project.json` to use `dbfs:/tmp/` path
- `dbfs:/tmp/` is typically allowed even with DBFS root restrictions
- Alternative: `dbfs:/FileStore/` or user-specific paths

### Solution 3: Updated Workflow Configuration
✅ **Updated**: GitHub Actions workflow to:
- Copy Free Edition configuration before deployment
- Set `MLFLOW_DEFAULT_ARTIFACT_ROOT=""` to use defaults
- Handle DBFS restrictions automatically

## Alternative Artifact Locations

If the above solutions don't work, try these locations in order:

### 1. MLflow Default (No artifact_location specified)
```json
{
    "environments": {
        "dev_feature": {
            "profile": "DEFAULT",
            "properties": {
                "workspace_directory": "/Users/shared/dbx/projects/we-pipeline_dev_feature"
            }
        }
    }
}
```

### 2. DBFS Temp Directory
```json
{
    "artifact_location": "dbfs:/tmp/dbx/we-pipeline_dev_feature"
}
```

### 3. DBFS FileStore
```json
{
    "artifact_location": "dbfs:/FileStore/shared_uploads/dbx/we-pipeline_dev_feature"
}
```

### 4. User-specific Path (Replace with your email)
```json
{
    "artifact_location": "dbfs:/Users/your.email@domain.com/dbx/we-pipeline_dev_feature"
}
```

### 5. For Unity Catalog Enabled Workspaces
```json
{
    "artifact_location": "dbfs:/Volumes/catalog/schema/volume/dbx/we-pipeline_dev_feature"
}
```

## How to Test Different Configurations

### Option 1: Test Locally with dbx
```bash
# Test with Free Edition config
cp .dbx/project_free_edition.json .dbx/project.json
dbx deploy --job=we-pipeline-rep-smoke-dev-feature-val-v1 --deployment-file=deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml --environment dev_feature --debug
```

### Option 2: Check Available Paths
In a Databricks notebook, run:
```python
# Check what DBFS paths are accessible
dbutils.fs.ls("dbfs:/")

# Test write access to different locations
test_locations = [
    "dbfs:/tmp/test_access",
    "dbfs:/FileStore/test_access", 
    f"dbfs:/Users/{dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()}/test_access"
]

for location in test_locations:
    try:
        dbutils.fs.put(f"{location}/test.txt", "test content")
        print(f"✅ {location} - WRITABLE")
        dbutils.fs.rm(f"{location}/test.txt")
    except Exception as e:
        print(f"❌ {location} - ERROR: {str(e)}")
```

## Verification Steps

1. **Check Configuration**:
   ```bash
   cat .dbx/project.json
   ```

2. **Test Deployment**:
   ```bash
   dbx deploy --dry-run --job=we-pipeline-rep-smoke-dev-feature-val-v1 --deployment-file=deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml --environment dev_feature
   ```

3. **Monitor GitHub Actions**:
   - Check if the workflow copies the Free Edition config successfully
   - Look for DBFS-related errors in deployment logs

## Quick Fix Commands

If you encounter the error again, run these commands in your project directory:

```bash
# Use the Free Edition configuration
cp .dbx/project_free_edition.json .dbx/project.json

# Or manually edit to remove artifact_location
sed -i '/"artifact_location"/d' .dbx/project.json

# Test the configuration
dbx deploy --dry-run --job=we-pipeline-rep-smoke-dev-feature-val-v1 --deployment-file=deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml --environment dev_feature
```

## Additional Notes

- **Free Edition**: Usually works best with MLflow default artifact location
- **Standard/Premium**: May allow more DBFS paths but still restrict root access
- **Unity Catalog**: Requires Volume-based paths (`dbfs:/Volumes/...`)
- **Security**: DBFS root restrictions are for security - use allowed paths only

## Files Modified

✅ `.dbx/project.json` - Updated with allowed artifact location
✅ `.dbx/project_free_edition.json` - Created Free Edition specific config
✅ `.github/workflows/qa_val.yml` - Updated to handle DBFS restrictions
✅ `DBFS_TROUBLESHOOTING.md` - This troubleshooting guide