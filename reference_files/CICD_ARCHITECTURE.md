# CI/CD Architecture - Databricks Asset Bundle (DAB) with GitHub Actions

## 🏗️ Architecture Overview

This project implements a modern CI/CD pipeline for Databricks using **Databricks Asset Bundles (DAB)**, which is the recommended approach for Databricks Enterprise deployments.

### **Technology Stack**
- **CI/CD Platform**: GitHub Actions
- **Deployment Method**: Databricks Asset Bundles (DAB)
- **Build System**: Python setuptools (wheel packages)
- **Orchestration**: Databricks Workflows
- **Version Control**: Git (GitHub)

---

## 📋 Key Components

### 1. **Databricks Asset Bundle Configuration** (`databricks.yml`)
The main configuration file that defines:
- Bundle name and workspace settings
- Target environments (dev_feature, staging, prod)
- Job definitions and tasks
- Artifact build instructions
- Resource configurations

### 2. **GitHub Actions Workflow** (`.github/workflows/qa_val.yml`)
Reusable workflow that:
- Sets up Python environment
- Installs Databricks CLI
- Builds Python wheel packages
- Validates bundle configuration
- Deploys to Databricks workspace
- Executes validation jobs

### 3. **Python Package** (`setup.py`)
Defines:
- Package metadata and dependencies
- Console script entry points
- Development dependencies
- Build configuration

---

## 🔄 CI/CD Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Checkout Code                                               │
│     - Clone repository                                          │
│     - Checkout specific branch/commit                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Environment Setup                                           │
│     - Install Python 3.10                                       │
│     - Install project dependencies                              │
│     - Install Databricks CLI (unified CLI)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Authentication                                              │
│     - Configure Databricks credentials                          │
│     - Set DATABRICKS_HOST and DATABRICKS_TOKEN                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Build Artifacts                                             │
│     - Run: python setup.py bdist_wheel                          │
│     - Generate .whl file in dist/                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Validate Bundle                                             │
│     - Run: databricks bundle validate -t dev_feature            │
│     - Check configuration syntax                                │
│     - Verify permissions and resources                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Deploy Bundle                                               │
│     - Run: databricks bundle deploy -t dev_feature              │
│     - Upload wheel to workspace                                 │
│     - Create/update jobs and resources                          │
│     - Apply configurations                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Execute Job (Optional)                                      │
│     - Run: databricks bundle run -t dev_feature <job_name>      │
│     - Execute validation tests                                  │
│     - Collect results                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Details

### **Environment Variables Required**
```yaml
DATABRICKS_HOST: https://<workspace>.databricks.com
DATABRICKS_TOKEN: dapi******************
GH_TOKEN: ghp_******************  # For private dependencies
```

### **Target Environments**
- `dev_feature`: Feature development environment
- `dev`: Development environment (if configured)
- `staging`: Staging environment (if configured)
- `prod`: Production environment (if configured)

---

## 🚀 Deployment Process

### **Manual Deployment (Local)**
```bash
# 1. Build wheel package
python setup.py bdist_wheel

# 2. Validate bundle configuration
databricks bundle validate -t dev_feature

# 3. Deploy to Databricks
databricks bundle deploy -t dev_feature

# 4. Run job
databricks bundle run -t dev_feature data_pipeline-rep-smoke-dev-feature-val-v1
```

### **Automated Deployment (GitHub Actions)**
Triggered on:
- Push to specific branches
- Pull request events
- Manual workflow dispatch
- Workflow call from parent workflows

---

## 🐛 Common Issues & Solutions

### **Issue 1: `databricks: command not found`**
**Cause**: PATH not persisted between GitHub Actions steps

**Solution**: Use the official Databricks CLI installation script and add to `$GITHUB_PATH`:
```yaml
- name: Install Databricks CLI
  run: |
    curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    echo "$HOME/.databrickscli" >> $GITHUB_PATH
```

### **Issue 2: Authentication Failures**
**Cause**: Wrong authentication method for DAB

**Solution**: Use `databricks configure --token` instead of manual config file:
```yaml
- name: Configure Databricks Authentication
  run: |
    databricks configure --token <<EOF
    ${{ secrets.DATABRICKS_HOST }}
    ${{ secrets.DATABRICKS_TOKEN }}
    EOF
```

### **Issue 3: Wheel Not Found**
**Cause**: Build step failed or wheel not in expected location

**Solution**: 
1. Ensure `python setup.py bdist_wheel` runs successfully
2. Verify wheel is in `dist/` directory
3. Check `databricks.yml` references correct path: `../dist/*.whl`

### **Issue 4: Job Configuration Errors**
**Cause**: Incorrect task configuration in `databricks.yml`

**Solution**: Use proper DAB job schema:
- Specify `new_cluster` or `existing_cluster_id`
- Define `python_wheel_task` with correct entry point
- List wheel in `libraries` section

---

## 📊 Best Practices

### ✅ **DO:**
1. Use Databricks Asset Bundles (DAB) for all deployments
2. Version your wheel packages semantically
3. Validate bundles before deployment
4. Use environment-specific configurations
5. Implement proper error handling in workflows
6. Store sensitive credentials in GitHub Secrets
7. Use reusable workflows for consistency
8. Document deployment procedures

### ❌ **DON'T:**
1. Use legacy `databricks-cli` package (use unified `databricks` CLI)
2. Hard-code credentials in workflow files
3. Skip validation steps
4. Deploy directly to production without testing
5. Mix DAB with legacy dbx deployment methods
6. Use `export PATH` in GitHub Actions (use `$GITHUB_PATH`)

---

## 🔍 Monitoring & Debugging

### **View Deployment Logs**
```bash
# Check job run status
databricks jobs runs list --job-id <job_id>

# Get run output
databricks jobs runs get-output --run-id <run_id>
```

### **Debug Bundle Issues**
```bash
# Validate with verbose output
databricks bundle validate -t dev_feature --debug

# Check deployed resources
databricks bundle summary -t dev_feature
```

### **GitHub Actions Debugging**
Enable debug logging:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

---

## 📚 Additional Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/index.html)
- [Databricks CLI Installation](https://docs.databricks.com/dev-tools/cli/install.html)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Python Wheel Packaging](https://packaging.python.org/tutorials/packaging-projects/)

---

## 🤝 Contributing

When making changes to the CI/CD pipeline:
1. Test changes in `dev_feature` environment first
2. Update this documentation
3. Create a pull request with detailed description
4. Ensure all checks pass before merging

---

## 📞 Support

For issues or questions:
- Check GitHub Actions workflow logs
- Review Databricks job run logs
- Consult team documentation
- Contact DevOps team

---

**Last Updated**: October 10, 2025
**Maintained By**: DataVerse & DataAvengers Team
