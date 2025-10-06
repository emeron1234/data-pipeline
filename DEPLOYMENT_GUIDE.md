# Databricks Free Edition Deployment Guide

## Prerequisites

### 1. GitHub Repository Secrets
Configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

- `DATABRICKS_HOST`: Your Databricks workspace URL (e.g., `https://community.cloud.databricks.com`)
- `DATABRICKS_TOKEN`: Personal access token from Databricks
- `GH_TOKEN`: GitHub personal access token (for repository access)

### 2. Databricks Free Edition Configuration

Since you're using Databricks Free Edition, you need to make the following adjustments:

#### Update Cluster Configuration
The current configuration uses `i3.2xlarge` which is not available in Free Edition. You need to modify the deployment files.

## Required Changes for Free Edition

### 1. Update Cluster Configuration in Deployment File

Edit `deployment_conf/validation/rep_smoke_deployment_dev_feature_val.yml`:

```yaml
custom:
  basic-cluster: &basic-cluster
    new_cluster:
      spark_version: "13.3.x-scala2.12"
      # Remove policy_id for Free Edition
      # policy_id: "784e7b5d-9f6e-4570-8530-8cc78d54dc66"
      
      # Use single node cluster for Free Edition
      num_workers: 0
      # Remove autoscale for Free Edition
      # autoscale:
      #   min_workers: 4
      #   max_workers: 8
      
      # Use available node type for Free Edition
      node_type_id: "i3.xlarge"  # or check available types in your workspace
      
      # Remove data_security_mode for Free Edition
      # data_security_mode: "SINGLE_USER"
      
      spark_conf:
        spark.databricks.adaptive.autoOptimizeShuffle.enabled: "true"
        # Remove Unity Catalog config for Free Edition
        # spark.databricks.unityCatalog.userIsolation.python.preview: "true"
        spark.cleaner.referenceTracking.cleanCheckpoints: "true"
        spark.hadoop.fs.s3a.multipart.size: 104857600
        spark.databricks.python.defaultPythonRepl: "pythonshell"
```

### 2. Update Access Control List (ACL)

For Free Edition, remove or simplify the ACL:

```yaml
# Remove or comment out ACL for Free Edition
# acl: &acl
#   access_control_list:
#     - service_principal_name: "98901d96-1aac-476a-a41f-08ebc08cb6af"
#       permission_level: "IS_OWNER"
#     - group_name: "SG-Altrata-Databricks-Development-Admin"
#       permission_level: "CAN_MANAGE"
#     - group_name: "SG-Altrata-Databricks-Development-Users"
#       permission_level: "CAN_MANAGE_RUN"
```

### 3. Update Workflow Definition

```yaml
environments:
  dev_feature:
    workflows:
      - name: "we-pipeline-rep-smoke-dev-feature-val-v1"
        # Remove ACL reference for Free Edition
        # <<: *acl
        job_clusters:
          - job_cluster_key: "default"
            <<: *basic-cluster
        # ... rest of the configuration
```

## How to Trigger the Job

### Method 1: Manual Trigger via GitHub Actions UI

1. Go to your GitHub repository
2. Click on "Actions" tab
3. Select "QA Validation Workflow Deployment"
4. Click "Run workflow"
5. Fill in the parameters:
   - **Environment**: `dev`
   - **Space**: `feature`
   - **Object type**: `re` (real estate)
   - **Job type**: `rep`
   - **Test type**: `smoke`
   - **Deploy**: `true`

### Method 2: Trigger via GitHub CLI

```bash
gh workflow run qa_workflow.yml \
  -f environment=dev \
  -f space=feature \
  -f object_type=re \
  -f job_type=rep \
  -f test_type=smoke \
  -f deploy=true
```

### Method 3: Trigger via API

```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/emeron1234/data-pipeline/actions/workflows/qa_workflow.yml/dispatches \
  -d '{
    "ref": "feature/hotfix_workflow_config",
    "inputs": {
      "environment": "dev",
      "space": "feature",
      "object_type": "re",
      "job_type": "rep",
      "test_type": "smoke",
      "deploy": "true"
    }
  }'
```

## Troubleshooting

### Common Issues with Free Edition

1. **Cluster Configuration**: Ensure you're using configurations compatible with Free Edition
2. **File Paths**: Use DBFS paths instead of Volumes for Free Edition
3. **Dependencies**: Make sure all Python dependencies are available
4. **Timeouts**: Free Edition has limitations on execution time

### Debugging Steps

1. Check GitHub Actions logs for deployment errors
2. Verify Databricks workspace configuration
3. Ensure all secrets are properly set
4. Check file paths and permissions in Databricks

## File Structure Requirements

Ensure your project structure matches:
```
data-pipeline/
├── main.py                          # Entry point
├── setup.py                         # Package configuration
├── data_pipeline/                   # Main package
│   ├── validation/                  # Validation modules
│   └── core/                        # Core utilities
├── deployment_conf/                 # Deployment configurations
│   └── validation/                  # Validation job configs
└── .github/workflows/               # GitHub Actions workflows
```

## Next Steps

1. Update the deployment configuration for Free Edition compatibility
2. Configure GitHub secrets
3. Test the workflow with a simple job first
4. Monitor execution in Databricks workspace
5. Adjust configurations based on Free Edition limitations