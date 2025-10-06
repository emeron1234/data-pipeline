# Databricks Free Edition Deployment Checklist

## Pre-requisites ✅

- [ ] Databricks Community Edition account created
- [ ] GitHub repository with the data pipeline code
- [ ] GitHub Secrets configured (see below)

## GitHub Secrets Configuration ✅

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

- [ ] **DATABRICKS_HOST**
  - Value: Your Databricks workspace URL
  - Example: `https://community.cloud.databricks.com`

- [ ] **DATABRICKS_TOKEN**
  - Value: Personal access token from Databricks
  - How to get: Databricks workspace → User Settings → Access tokens → Generate new token

- [ ] **GH_TOKEN**
  - Value: GitHub personal access token
  - How to get: GitHub → Settings → Developer settings → Personal access tokens

## File Modifications for Free Edition ✅

- [ ] **Update deployment configuration**
  - Use the Free Edition compatible file: `rep_smoke_deployment_dev_feature_val_free_edition.yml`
  - Remove `policy_id`, `autoscale`, `data_security_mode`
  - Set `num_workers: 0` for single-node cluster
  - Use available node type (check your Databricks workspace)

- [ ] **Update workflow file**
  - Modified `qa_workflow.yml` to use Free Edition deployment file
  - ✅ Already updated to use `_free_edition.yml` suffix

## Triggering the Job ✅

### Option 1: GitHub Actions UI
1. [ ] Go to your GitHub repository
2. [ ] Click "Actions" tab
3. [ ] Select "QA Validation Workflow Deployment"
4. [ ] Click "Run workflow"
5. [ ] Fill parameters:
   - Environment: `dev`
   - Space: `feature`
   - Object type: `re`
   - Job type: `rep`
   - Test type: `smoke`
   - Deploy: `true`

### Option 2: GitHub CLI
```bash
gh workflow run qa_workflow.yml \
  -f environment=dev \
  -f space=feature \
  -f object_type=re \
  -f job_type=rep \
  -f test_type=smoke \
  -f deploy=true
```

### Option 3: REST API
```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/emeron1234/data-pipeline/actions/workflows/qa_workflow.yml/dispatches \
  -d '{"ref": "feature/hotfix_workflow_config", "inputs": {"environment": "dev", "space": "feature", "object_type": "re", "job_type": "rep", "test_type": "smoke", "deploy": "true"}}'
```

## Monitoring and Troubleshooting ✅

- [ ] **Check GitHub Actions logs**
  - Go to Actions tab → Select workflow run → View logs

- [ ] **Check Databricks workspace**
  - Go to Workflows tab in Databricks
  - Look for your deployed job
  - Monitor execution status

- [ ] **Common Free Edition limitations to check**
  - Single-node clusters only
  - Limited execution time
  - No Unity Catalog features
  - Limited storage options (use DBFS instead of Volumes)

## Verification Steps ✅

- [ ] Workflow deploys successfully in GitHub Actions
- [ ] Job appears in Databricks workspace
- [ ] Job executes without cluster errors
- [ ] Check job logs in Databricks for application errors
- [ ] Verify data processing results

## Next Steps ✅

- [ ] Test with a simple validation job first
- [ ] Gradually add more complex validations
- [ ] Monitor performance and adjust cluster configuration if needed
- [ ] Set up notifications for job success/failure

## Files Created/Modified ✅

- ✅ `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- ✅ `rep_smoke_deployment_dev_feature_val_free_edition.yml` - Free Edition compatible deployment
- ✅ `setup_free_edition.sh` - Setup script
- ✅ `qa_workflow.yml` - Updated to use Free Edition deployment file
- ✅ `DEPLOYMENT_CHECKLIST.md` - This checklist

## Support Resources ✅

- [Databricks Community Edition Documentation](https://docs.databricks.com/getting-started/community-edition.html)
- [dbx Documentation](https://dbx.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Note**: Make sure to test the deployment in a development environment first before running production workloads.