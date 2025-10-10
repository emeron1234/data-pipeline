# Migration Guide: dbx to Databricks Asset Bundles (DAB)

## 📋 Overview

This document describes the migration from the legacy **dbx deployment format** to the modern **Databricks Asset Bundles (DAB)** format.

**Migration Date**: October 10, 2025  
**Status**: ✅ Complete

---

## 🔄 What Changed

### **Before: dbx Format**
- Used separate deployment files in `deployment_conf/`
- Configuration used `environments` and `workflows` keys
- Required `dbx deploy` and `dbx launch` commands
- Mixed Python package and Databricks configuration

### **After: DAB Format**
- Single `databricks.yml` configuration file at project root
- Configuration uses `targets` and `resources` keys
- Uses `databricks bundle` commands
- Clean separation of concerns

---

## 📁 File Changes

### **1. Removed/Deprecated Files**

| File | Status | Action |
|------|--------|--------|
| `deployment_conf/validation/rep_smoke_deployment_dev_feature_val.yml` | Deprecated | Commented out, kept for reference |

### **2. Modified Files**

| File | Change |
|------|--------|
| `databricks.yml` | Removed `include` directive, added full job definition |
| `.github/workflows/qa_val.yml` | Updated CLI installation and commands |

### **3. New Files**

| File | Purpose |
|------|---------|
| `CICD_ARCHITECTURE.md` | Architecture documentation |
| `DEPLOYMENT_FIXES.md` | Issue analysis and fixes |
| `MIGRATION_DBX_TO_DAB.md` | This migration guide |

---

## 🔀 Configuration Mapping

### **Old dbx Format** (`deployment_conf/validation/rep_smoke_deployment_dev_feature_val.yml`)
```yaml
environments:
  dev_feature:
    workflows:
      - name: "data_pipeline-rep-smoke-dev-feature-val-v1"
        tasks:
          - task_key: "rep_dev_feature_validation_task"
            python_wheel_task:
              package_name: "data_pipeline"
              entry_point: "data-pipeline-etl"
              parameters: [...]
            environment_key: "default"
        environments:
          - environment_key: "default"
            spec:
              client: "1"
              dependencies:
                - "dist/data_pipeline-1.0.1-py3-none-any.whl"
```

### **New DAB Format** (`databricks.yml`)
```yaml
bundle:
  name: "data_pipeline"

targets:
  dev_feature:
    mode: development
    workspace:
      root_path: "/Shared/dbx/projects/data-pipeline_dev_feature_v2"
    
    artifacts:
      default:
        type: whl
        build: python setup.py bdist_wheel
        path: ./dist/*.whl
    
    resources:
      jobs:
        data_pipeline-rep-smoke-dev-feature-val-v1:
          name: "data_pipeline-rep-smoke-dev-feature-val-v1"
          tasks:
            - task_key: "rep_dev_feature_validation_task"
              job_cluster_key: "default_cluster"
              python_wheel_task:
                package_name: "data_pipeline"
                entry_point: "data-pipeline-etl"
                parameters: [...]
              libraries:
                - whl: ../dist/*.whl
          
          job_clusters:
            - job_cluster_key: "default_cluster"
              new_cluster:
                spark_version: "13.3.x-scala2.12"
                node_type_id: "Standard_DS3_v2"
                num_workers: 1
```

---

## 🔧 Command Changes

### **Deployment Commands**

| Task | Old dbx Command | New DAB Command |
|------|-----------------|-----------------|
| Validate | `dbx deploy --deployment-file <file>` | `databricks bundle validate -t <target>` |
| Deploy | `dbx deploy --deployment-file <file> --environment <env>` | `databricks bundle deploy -t <target>` |
| Run Job | `dbx launch --environment <env> --job <job>` | `databricks bundle run -t <target> <job>` |
| List Jobs | `dbx execute --cluster-name <cluster> --job <job>` | `databricks jobs list` |

### **CLI Installation**

| Aspect | Old dbx | New DAB |
|--------|---------|---------|
| Package | `pip install dbx` | Official installer script |
| Command | `dbx` | `databricks` |
| Config | `~/.databrickscfg` or project file | `databricks configure` |

---

## ⚙️ GitHub Actions Changes

### **Before:**
```yaml
- name: Install dbx
  run: pip install dbx

- name: Deploy with dbx
  run: |
    dbx deploy --deployment-file ./deployment_conf/validation/rep_smoke_deployment_dev_feature_val.yml \
      --environment dev_feature

- name: Launch Job
  run: |
    dbx launch --environment dev_feature \
      --job data_pipeline-rep-smoke-dev-feature-val-v1
```

### **After:**
```yaml
- name: Install Databricks CLI
  run: |
    curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    echo "$HOME/.databrickscli" >> $GITHUB_PATH

- name: Validate Bundle Configuration
  run: databricks bundle validate -t dev_feature

- name: Deploy Bundle
  run: databricks bundle deploy -t dev_feature

- name: Run Job
  run: databricks bundle run -t dev_feature data_pipeline-rep-smoke-dev-feature-val-v1
```

---

## 🎯 Key Benefits of DAB

### **1. Unified Configuration**
- All resources in one place (`databricks.yml`)
- No need to manage multiple deployment files
- Easier to understand project structure

### **2. Better Validation**
- Built-in validation before deployment
- Schema validation for configuration
- Catch errors early

### **3. Official Support**
- DAB is the official Databricks deployment method
- dbx is community-maintained (deprecated path)
- Better integration with Databricks platform

### **4. Enhanced Features**
- Native support for all Databricks resources (jobs, pipelines, etc.)
- Better dependency management
- Improved artifact handling

### **5. Cleaner CI/CD**
- Simpler workflow files
- Fewer dependencies
- More reliable deployments

---

## ✅ Validation Steps

After migration, verify:

1. **Configuration is valid:**
   ```bash
   databricks bundle validate -t dev_feature
   ```

2. **Deployment succeeds:**
   ```bash
   databricks bundle deploy -t dev_feature
   ```

3. **Job exists in workspace:**
   ```bash
   databricks jobs list | grep "data_pipeline-rep-smoke-dev-feature-val-v1"
   ```

4. **Job runs successfully:**
   ```bash
   databricks bundle run -t dev_feature data_pipeline-rep-smoke-dev-feature-val-v1
   ```

---

## 🔍 Troubleshooting

### **Issue: "unknown field: workflows"**
**Cause**: Old dbx format file still being included  
**Solution**: Remove `include` directive from `databricks.yml` or comment out old deployment files

### **Issue: "both 'environments' and 'targets' are specified"**
**Cause**: Mixing old and new formats  
**Solution**: Use only `targets` in DAB format, remove `environments` from included files

### **Issue: "databricks: command not found"**
**Cause**: CLI not installed or not in PATH  
**Solution**: Use official installation script and add to `$GITHUB_PATH`

### **Issue: Job configuration errors**
**Cause**: Invalid DAB schema  
**Solution**: Run `databricks bundle validate` and fix reported issues

---

## 📚 Additional Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/index.html)
- [DAB Schema Reference](https://docs.databricks.com/dev-tools/bundles/reference.html)
- [Migration from dbx](https://docs.databricks.com/dev-tools/bundles/migrate-from-dbx.html)
- [CI/CD with DAB](https://docs.databricks.com/dev-tools/bundles/ci-cd.html)

---

## 📞 Support

For questions or issues with the migration:
1. Review this migration guide
2. Check `CICD_ARCHITECTURE.md` for architecture details
3. Check `DEPLOYMENT_FIXES.md` for common issues
4. Contact the DataVerse/DataAvengers team

---

## 🔄 Future Migrations

If you have other deployment files in `deployment_conf/`:

1. **Identify all dbx deployment files:**
   ```bash
   find deployment_conf/ -name "*.yml"
   ```

2. **For each file:**
   - Extract the job configuration
   - Add to `databricks.yml` under appropriate target
   - Comment out or remove old file
   - Test deployment

3. **Update documentation:**
   - Update runbooks
   - Update team procedures
   - Train team on new commands

---

**Migration Completed By**: GitHub Copilot  
**Verified By**: [To be filled]  
**Production Deployment Date**: [To be scheduled]
