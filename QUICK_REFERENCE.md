# Quick Reference: DAB Deployment Commands

## 🚀 Common Commands

### **Local Development**

```bash
# 1. Build the wheel package
python setup.py bdist_wheel

# 2. Validate bundle configuration (always do this first!)
databricks bundle validate -t dev_feature

# 3. Deploy to Databricks
databricks bundle deploy -t dev_feature

# 4. Run the job
databricks bundle run -t dev_feature data_pipeline-rep-smoke-dev-feature-val-v1

# 5. Check deployment summary
databricks bundle summary -t dev_feature
```

---

## 🔍 Validation & Debugging

```bash
# Validate with verbose output
databricks bundle validate -t dev_feature --debug

# Check what would be deployed (dry run)
databricks bundle deploy -t dev_feature --dry-run

# View deployed resources
databricks bundle summary -t dev_feature

# Check CLI version
databricks --version

# View authentication profiles
databricks auth profiles
```

---

## 📊 Job Management

```bash
# List all jobs
databricks jobs list

# Get job details
databricks jobs get --job-id <job_id>

# List recent runs
databricks jobs runs list --job-id <job_id>

# Get run output
databricks jobs runs get-output --run-id <run_id>

# Cancel a running job
databricks jobs runs cancel --run-id <run_id>
```

---

## 🔧 Cluster Management

```bash
# List clusters
databricks clusters list

# Get cluster details
databricks clusters get --cluster-id <cluster_id>

# Start a cluster
databricks clusters start --cluster-id <cluster_id>

# Stop a cluster
databricks clusters delete --cluster-id <cluster_id>
```

---

## 🏗️ Workspace Management

```bash
# List workspace files
databricks workspace list /Shared/dbx/projects/data-pipeline_dev_feature_v2

# Upload a file
databricks workspace upload <local_file> <workspace_path>

# Download a file
databricks workspace download <workspace_path> <local_file>

# Delete a file
databricks workspace delete <workspace_path>
```

---

## 🔑 Authentication

```bash
# Configure with token (interactive)
databricks configure --token

# Configure with environment variables
export DATABRICKS_HOST="https://<workspace>.databricks.com"
export DATABRICKS_TOKEN="dapi******************"

# Or create a profile
databricks auth login --host https://<workspace>.databricks.com
```

---

## 📦 Artifacts & Libraries

```bash
# List uploaded wheels
databricks fs ls dbfs:/FileStore/jars/

# Upload a wheel manually (usually DAB does this)
databricks fs cp dist/data_pipeline-1.0.1-py3-none-any.whl dbfs:/FileStore/jars/

# List libraries on cluster
databricks libraries cluster-status --cluster-id <cluster_id>
```

---

## 🎯 Target-Specific Deployments

```bash
# Deploy to dev_feature
databricks bundle deploy -t dev_feature

# Deploy to staging (if configured)
databricks bundle deploy -t staging

# Deploy to production (if configured)
databricks bundle deploy -t prod
```

---

## 🔄 CI/CD Pipeline Commands

These are the exact commands used in GitHub Actions:

```bash
# 1. Install Databricks CLI
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# 2. Configure authentication
databricks configure --token <<EOF
${DATABRICKS_HOST}
${DATABRICKS_TOKEN}
EOF

# 3. Build wheel
python setup.py bdist_wheel

# 4. Validate bundle
databricks bundle validate -t dev_feature

# 5. Deploy bundle
databricks bundle deploy -t dev_feature

# 6. Run job (optional)
databricks bundle run -t dev_feature data_pipeline-rep-smoke-dev-feature-val-v1
```

---

## ⚠️ Troubleshooting

### **Command not found**
```bash
# Check if CLI is installed
which databricks

# Check PATH
echo $PATH

# Reinstall if needed
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
```

### **Authentication errors**
```bash
# Check current profile
databricks auth profiles

# Test connection
databricks workspace list /

# Reconfigure
databricks configure --token
```

### **Validation errors**
```bash
# Get detailed validation output
databricks bundle validate -t dev_feature --debug

# Check schema
databricks bundle schema

# Verify workspace path exists
databricks workspace list /Shared/dbx/projects/
```

### **Deployment fails**
```bash
# Check workspace permissions
databricks workspace get-status /Shared/dbx/projects/data-pipeline_dev_feature_v2

# Verify wheel was built
ls -lh dist/

# Check deployed resources
databricks bundle summary -t dev_feature
```

---

## 📋 Pre-Deployment Checklist

- [ ] Code changes committed and pushed
- [ ] Wheel builds successfully (`python setup.py bdist_wheel`)
- [ ] Bundle validates (`databricks bundle validate -t dev_feature`)
- [ ] Authentication configured (`databricks auth profiles`)
- [ ] Correct target selected (`dev_feature`, `staging`, or `prod`)
- [ ] No uncommitted changes (if using version control in bundle)

---

## 🔗 Quick Links

- [databricks.yml](./databricks.yml) - Main bundle configuration
- [CICD_ARCHITECTURE.md](./CICD_ARCHITECTURE.md) - Full architecture docs
- [DEPLOYMENT_FIXES.md](./DEPLOYMENT_FIXES.md) - Common issues & fixes
- [MIGRATION_DBX_TO_DAB.md](./MIGRATION_DBX_TO_DAB.md) - Migration guide

---

## 📱 One-Liner Deploy

For quick deployments (after initial setup):

```bash
python setup.py bdist_wheel && databricks bundle validate -t dev_feature && databricks bundle deploy -t dev_feature
```

---

**Last Updated**: October 10, 2025  
**Target Environment**: `dev_feature`  
**Job Name**: `data_pipeline-rep-smoke-dev-feature-val-v1`
