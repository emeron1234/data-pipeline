# Workspace Host Interpolation Error - Fix Guide

## 🔴 Error Message

```
Warning: Variable interpolation is not supported for fields that configure authentication
  at workspace.host
  in databricks.yml:6:9

Interpolation is not supported for the field workspace.host. Please set
the DATABRICKS_HOST environment variable if you wish to configure this field at runtime.

Error: failed during request visitor: parse "https://${workspace.host}": invalid character "{" in host name
```

---

## 🔍 Root Cause

### **The Problem**
DAB (Databricks Asset Bundles) has specific fields that handle authentication, and these fields **do not support variable interpolation**.

**Authentication fields that don't support interpolation:**
- `workspace.host`
- `workspace.token`
- Any field used for initial connection/authentication

### **Why It Fails**
When you write:
```yaml
workspace:
  host: ${workspace.host}
```

DAB tries to:
1. Parse the configuration file
2. Extract `workspace.host` to connect to Databricks
3. But finds `${workspace.host}` (a variable placeholder)
4. Tries to parse `https://${workspace.host}` as a URL
5. **Fails** because `{` is an invalid character in a hostname

---

## ✅ Solution

### **Option 1: Remove workspace.host (Recommended)**

Let DAB automatically use the `DATABRICKS_HOST` environment variable:

```yaml
bundle:
  name: "data_pipeline"

# No workspace section needed - uses DATABRICKS_HOST env var

targets:
  dev_feature:
    mode: development
    workspace:
      root_path: "/Shared/dbx/projects/data-pipeline_dev_feature_v2"
    
    resources:
      jobs:
        # ... job definitions
```

**How it works:**
1. GitHub Actions sets `DATABRICKS_HOST` environment variable
2. You run `databricks configure --token` which stores the host
3. DAB automatically uses the authenticated profile's host
4. No need to specify it in `databricks.yml`

---

### **Option 2: Use Hardcoded Value (Not Recommended)**

If you must specify the host in the file:

```yaml
workspace:
  host: "https://your-workspace.databricks.com"  # Hardcoded

targets:
  dev_feature:
    # ...
```

**Drawbacks:**
- ❌ Not portable across environments
- ❌ Needs to be changed for each workspace
- ❌ Doesn't work well with multi-environment setups
- ❌ Secrets exposed in repository

---

### **Option 3: Use Target-Specific Host (Advanced)**

Define different hosts per target:

```yaml
bundle:
  name: "data_pipeline"

targets:
  dev_feature:
    mode: development
    workspace:
      host: "https://dev-workspace.databricks.com"
      root_path: "/Shared/dbx/projects/data-pipeline_dev_feature_v2"
  
  production:
    mode: production
    workspace:
      host: "https://prod-workspace.databricks.com"
      root_path: "/Shared/dbx/projects/data-pipeline_prod"
```

**Use case:** When you have different Databricks workspaces for different environments.

---

## 🔧 Implementation in Your Project

### **Current State (Fixed)**

```yaml
bundle:
  name: "data_pipeline"

# Authentication handled by environment variables

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
          # ... job configuration
```

### **GitHub Actions Workflow**

```yaml
jobs:
  qa-deploy-config:
    env:
      DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
      DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
    
    steps:
      # ... other steps
      
      - name: Configure Databricks Authentication
        run: |
          databricks configure --token <<EOF
          ${{ secrets.DATABRICKS_HOST }}
          ${{ secrets.DATABRICKS_TOKEN }}
          EOF
      
      - name: Validate Bundle Configuration
        run: databricks bundle validate -t dev_feature
        # ✅ Now uses DATABRICKS_HOST from environment
```

---

## 🧪 Verification

After removing the invalid interpolation:

### **1. Validate Locally**
```bash
# Set environment variable
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="dapi******************"

# Configure CLI
databricks configure --token <<EOF
${DATABRICKS_HOST}
${DATABRICKS_TOKEN}
EOF

# Validate bundle
databricks bundle validate -t dev_feature
```

**Expected Output:**
```
Name: data_pipeline
Target: dev_feature
Workspace:
  Host: https://your-workspace.databricks.com  # ✅ Actual value, not placeholder
  Path: /Shared/dbx/projects/data-pipeline_dev_feature_v2

Validation OK!
```

### **2. Verify in CI/CD**

Check GitHub Actions logs for:
```
✅ No warnings about variable interpolation
✅ Host shows actual URL, not ${workspace.host}
✅ Validation passes without errors
✅ Deploy succeeds
```

---

## 📚 Understanding DAB Authentication

### **How DAB Determines Workspace Host**

Priority order:
1. **Command line flag**: `databricks bundle deploy --host https://...`
2. **Target-specific host**: In `databricks.yml` under `targets.<name>.workspace.host`
3. **Bundle-level host**: In `databricks.yml` under `workspace.host` (not recommended)
4. **Environment variable**: `DATABRICKS_HOST`
5. **CLI profile**: From `~/.databrickscfg` or authentication profile
6. **Error**: If none of the above are set

### **Recommended Approach**

Use **#4 (Environment variable)** or **#5 (CLI profile)**:

```bash
# In GitHub Actions
env:
  DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
  DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}

# Or configure profile once
databricks configure --token
```

---

## 🐛 Common Mistakes

### ❌ **Don't Do This:**
```yaml
workspace:
  host: ${DATABRICKS_HOST}          # Wrong syntax
  host: ${workspace.host}           # Recursive reference
  host: $DATABRICKS_HOST            # Shell variable syntax
  host: {{workspace.host}}          # Template syntax
```

### ✅ **Do This Instead:**
```yaml
# Option 1: Don't specify host (recommended)
bundle:
  name: "data_pipeline"

targets:
  dev_feature:
    workspace:
      root_path: "/path/to/project"

# Option 2: Hardcode if necessary
workspace:
  host: "https://your-workspace.databricks.com"

# Option 3: Per-target specification
targets:
  dev:
    workspace:
      host: "https://dev.databricks.com"
      root_path: "/dev/project"
  prod:
    workspace:
      host: "https://prod.databricks.com"
      root_path: "/prod/project"
```

---

## 🔗 Related Documentation

- [DAB Configuration Reference](https://docs.databricks.com/dev-tools/bundles/settings.html)
- [DAB Authentication](https://docs.databricks.com/dev-tools/auth/index.html)
- [Environment Variables in DAB](https://docs.databricks.com/dev-tools/bundles/work-with-variables.html)

---

## 📋 Checklist

After applying the fix:
- [ ] Removed `workspace.host` from bundle level
- [ ] Set `DATABRICKS_HOST` in GitHub Actions environment
- [ ] Configured authentication with `databricks configure --token`
- [ ] Validated bundle: `databricks bundle validate -t dev_feature`
- [ ] Checked that validation shows actual host, not placeholder
- [ ] Deployed successfully: `databricks bundle deploy -t dev_feature`

---

**Issue Fixed:** October 10, 2025  
**Status:** ✅ Resolved  
**Next:** Proceed with deployment testing
