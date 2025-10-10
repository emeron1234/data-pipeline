# CLI Version Conflict Fix - Summary

## 🔴 Problem

**Warning Message:**
```
Databricks CLI v0.272.0 found at /usr/local/bin/databricks
Your current $PATH prefers running CLI v0.17.8 at /opt/hostedtoolcache/Python/3.10.18/x64/bin/databricks

Because both are installed and available in $PATH, I assume you are trying to run the newer version.
If you want to disable this behavior you can set DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION=1.
```

## 🔍 Root Cause

### **Multiple CLI Installations Detected:**

1. **Legacy CLI v0.17.8** (pip-installed)
   - Location: `/opt/hostedtoolcache/Python/3.10.18/x64/bin/databricks`
   - Installed via: `pip install databricks` (old/legacy package)
   - Found first in PATH (higher priority)
   - **Not compatible with DAB**

2. **Unified CLI v0.272.0** (official installation)
   - Location: `/usr/local/bin/databricks`
   - Installed via: Official installation script
   - Found second in PATH (lower priority)
   - **Required for DAB**

### **Why This Happens:**

The GitHub Actions runner can have Python packages pre-installed or installed by previous steps. When you run:
```bash
pip install -e ".[dev]"
```

If any of your dependencies (in `setup.py`) or their sub-dependencies install the old `databricks` or `databricks-cli` package, it gets installed to the Python site-packages directory, which is typically in PATH before `/usr/local/bin`.

## ✅ Solution Applied

### **1. Set Global Environment Variable**

Added to job-level environment variables:
```yaml
jobs:
  qa-deploy-config:
    env:
      DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION: "1"
```

**Effect:** Suppresses the version warning message globally for all steps.

### **2. Remove Legacy CLI**

Added explicit cleanup step:
```yaml
- name: Remove Legacy Databricks CLI
  run: |
    pip uninstall -y databricks-cli databricks || true
    echo "✅ Removed any legacy Databricks CLI installations"
```

**Effect:** Removes any pip-installed Databricks CLI packages before installing the unified CLI.

### **3. Fix PATH Priority**

Modified installation step:
```yaml
- name: Install Databricks CLI
  run: |
    curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    # Prepend the new CLI path to ensure it's used first
    echo "/usr/local/bin" >> $GITHUB_PATH
    echo "$HOME/.databrickscli" >> $GITHUB_PATH
```

**Effect:** Ensures `/usr/local/bin` (where unified CLI is installed) is checked first in PATH.

## 🎯 How It Works

### **Before Fix:**

```
PATH Priority:
1. /opt/hostedtoolcache/Python/3.10.18/x64/bin  ← Old CLI v0.17.8 (used)
2. /usr/local/bin                               ← New CLI v0.272.0 (ignored)

Result: Warning message appears, potentially wrong CLI used
```

### **After Fix:**

```
PATH Priority:
1. /usr/local/bin                               ← New CLI v0.272.0 (used) ✅
2. $HOME/.databrickscli                         ← Backup location
3. /opt/hostedtoolcache/Python/3.10.18/x64/bin  ← Old CLI removed anyway

Result: Correct CLI used, no warning
```

## 🧪 Verification Steps

The workflow now includes a verification step:
```yaml
- name: Verify Databricks CLI
  run: |
    which databricks
    databricks --version
    databricks auth profiles
```

**Expected Output:**
```
/usr/local/bin/databricks
Databricks CLI v0.272.0
```

## 📊 Complete Fix Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Install Python Dependencies                            │
│     - Includes setup.py dependencies                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Remove Legacy Databricks CLI                           │
│     - pip uninstall databricks-cli databricks              │
│     - Ensures clean slate                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Install Unified Databricks CLI                         │
│     - Via official installation script                      │
│     - Installs to /usr/local/bin                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Fix PATH Priority                                       │
│     - Prepend /usr/local/bin to PATH                       │
│     - Add ~/.databrickscli as backup                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Verify Installation                                     │
│     - Check which CLI is being used                         │
│     - Verify version (should be v0.272.0+)                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  6. All Subsequent Steps Use Correct CLI                   │
│     - Configure authentication                              │
│     - Validate bundle                                       │
│     - Deploy bundle                                         │
│     - Run jobs                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Environment Variable Explanation

### **DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION**

**Purpose:** Controls the automatic execution behavior when multiple CLI versions are detected.

**Values:**
- `"0"` or unset (default): Shows warning and automatically uses newer version
- `"1"`: Suppresses warning and uses the version found first in PATH

**Our Setting:** `"1"`

**Why:** 
- We've already ensured the correct version is first in PATH
- We don't need the warning since we've explicitly cleaned up old versions
- Keeps logs cleaner and less confusing

## 🛡️ Prevention for Local Development

If you're developing locally and encounter the same issue:

### **Option 1: Remove pip-installed CLI**
```bash
pip uninstall -y databricks-cli databricks
```

### **Option 2: Install unified CLI**
```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Windows
winget install Databricks.CLI
```

### **Option 3: Set environment variable**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION=1
```

## 📋 Checklist for Future Projects

When setting up Databricks CI/CD:

- [ ] Don't install Databricks CLI via pip
- [ ] Use official installation script only
- [ ] Add cleanup step to remove legacy CLI
- [ ] Prepend correct path to $GITHUB_PATH
- [ ] Set `DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION=1`
- [ ] Add verification step to check CLI version
- [ ] Test in dev environment first

## 🔗 Related Files

- `.github/workflows/qa_val.yml` - Fixed workflow
- `DEPLOYMENT_FIXES.md` - Complete fix documentation
- `CICD_ARCHITECTURE.md` - Architecture overview

## 📚 References

- [Databricks CLI Installation](https://docs.databricks.com/dev-tools/cli/install.html)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html)
- [GitHub Actions PATH Management](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#adding-a-system-path)

---

**Fixed Date:** October 10, 2025  
**Issue Status:** ✅ Resolved  
**Verified:** Pending next workflow run
