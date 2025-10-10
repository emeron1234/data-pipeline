# Visual Architecture Diagram

## 🏗️ Complete CI/CD Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GITHUB REPOSITORY                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Branch: feature/hotfix_workflow_config                          │  │
│  │                                                                   │  │
│  │  📁 .github/workflows/qa_val.yml  ← Workflow Definition          │  │
│  │  📁 databricks.yml                ← DAB Configuration            │  │
│  │  📁 setup.py                      ← Python Package Config        │  │
│  │  📁 data_pipeline/                ← Application Code             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Push/PR/Manual Trigger
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS RUNNER                            │
│                         (Ubuntu 24.04 VM)                               │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ STEP 1: Environment Setup                                        │ │
│  │  • Checkout code                                                 │ │
│  │  • Install Python 3.10                                           │ │
│  │  • Install project dependencies                                  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ STEP 2: Clean Legacy CLI (FIX #3)                                │ │
│  │  ❌ Remove: databricks-cli v0.17.8                               │ │
│  │  ❌ Remove: any pip-installed databricks packages                │ │
│  │  ✅ Result: Clean environment                                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ STEP 3: Install Unified CLI (FIX #1)                             │ │
│  │  📥 Download: setup-cli/main/install.sh                          │ │
│  │  ⚙️  Install: Databricks CLI v0.272.0+                           │ │
│  │  📍 Location: /usr/local/bin/databricks                          │ │
│  │  🛤️  PATH: Prepend /usr/local/bin to $GITHUB_PATH                │ │
│  │  ✅ Set: DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION=1           │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ STEP 4: Configure Authentication                                 │ │
│  │  🔑 Input: DATABRICKS_HOST (from secrets)                        │ │
│  │  🔑 Input: DATABRICKS_TOKEN (from secrets)                       │ │
│  │  ⚙️  Run: databricks configure --token                           │ │
│  │  ✅ Result: ~/.databrickscfg created                              │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ STEP 5: Verify Installation                                      │ │
│  │  📍 which databricks → /usr/local/bin/databricks                 │ │
│  │  📦 databricks --version → v0.272.0                               │ │
│  │  👤 databricks auth profiles → [list profiles]                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ STEP 6: Build Artifacts                                          │ │
│  │  🔨 Run: python setup.py bdist_wheel                             │ │
│  │  📦 Output: dist/data_pipeline-1.0.x-py3-none-any.whl            │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ STEP 7: Validate Bundle (FIX #2)                                 │ │
│  │  🔍 Run: databricks bundle validate -t dev_feature               │ │
│  │  📋 Check: databricks.yml syntax                                 │ │
│  │  🔐 Check: Permissions & access                                  │ │
│  │  ✅ Result: Validation passed (no 'environments' error)          │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│                                  │ All checks passed ✅                 │
│                                  ▼                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Deploy via Databricks API
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATABRICKS WORKSPACE                               │
│                 (https://<workspace>.databricks.com)                    │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ DEPLOYMENT PROCESS                                                │ │
│  │                                                                   │ │
│  │  1. Upload Wheel Package                                         │ │
│  │     📦 dist/data_pipeline-1.0.x-py3-none-any.whl                 │ │
│  │     → /Shared/dbx/projects/data-pipeline_dev_feature_v2/         │ │
│  │                                                                   │ │
│  │  2. Create/Update Job                                            │ │
│  │     📋 Name: data_pipeline-rep-smoke-dev-feature-val-v1          │ │
│  │     ⚙️  Task: rep_dev_feature_validation_task                    │ │
│  │     🎯 Entry Point: data-pipeline-etl                            │ │
│  │                                                                   │ │
│  │  3. Configure Cluster                                            │ │
│  │     💻 Type: Job Cluster (serverless)                            │ │
│  │     ⚡ Spark: 13.3.x-scala2.12                                   │ │
│  │     📊 Node: Standard_DS3_v2                                     │ │
│  │     👥 Workers: 1                                                │ │
│  │                                                                   │ │
│  │  4. Attach Libraries                                             │ │
│  │     📚 Wheel: data_pipeline-1.0.x-py3-none-any.whl              │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│                                  │ Deployment Complete ✅               │
│                                  ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ CREATED RESOURCES                                                 │ │
│  │                                                                   │ │
│  │  📁 /Shared/dbx/projects/data-pipeline_dev_feature_v2/           │ │
│  │     ├── 📦 data_pipeline-1.0.x-py3-none-any.whl                  │ │
│  │     └── 📋 Job Configuration                                     │ │
│  │                                                                   │ │
│  │  🔧 Workflows → Jobs                                             │ │
│  │     └── data_pipeline-rep-smoke-dev-feature-val-v1               │ │
│  │         ├── Status: Ready                                        │ │
│  │         ├── Cluster: Configured                                  │ │
│  │         └── Libraries: Attached                                  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│                                  │ Optional: Run Job                    │
│                                  ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ JOB EXECUTION (if not skipped)                                   │ │
│  │                                                                   │ │
│  │  🚀 Trigger: databricks bundle run -t dev_feature <job>          │ │
│  │  ⚙️  Execute: data_pipeline.validation.task.rep_val              │ │
│  │  📊 Parameters:                                                   │ │
│  │     • --env dev                                                  │ │
│  │     • --space feature                                            │ │
│  │     • --object_type re                                           │ │
│  │     • --job_type rep                                             │ │
│  │     • --test_type smoke                                          │ │
│  │                                                                   │ │
│  │  📈 Monitor: Real-time logs in Databricks UI                     │ │
│  │  ✅ Result: Job completed successfully                            │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Return results
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS RUNNER                            │
│                                                                         │
│  ✅ All steps completed successfully                                    │
│  📊 Deployment logs available                                           │
│  🎉 Workflow finished: SUCCESS                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
   ┌─────────────┐
   │   GitHub    │
   │  Repository │
   └──────┬──────┘
          │
          │ 1. Code push/PR
          ▼
   ┌─────────────┐
   │   GitHub    │
   │   Actions   │◄────── Secrets (HOST, TOKEN)
   └──────┬──────┘
          │
          │ 2. Build wheel
          ▼
   ┌─────────────┐
   │   .whl      │
   │   Package   │
   └──────┬──────┘
          │
          │ 3. Bundle deploy
          ▼
   ┌─────────────┐
   │ Databricks  │
   │  Workspace  │
   └──────┬──────┘
          │
          │ 4. Create/Update job
          ▼
   ┌─────────────┐
   │ Databricks  │
   │     Job     │
   └──────┬──────┘
          │
          │ 5. Execute (optional)
          ▼
   ┌─────────────┐
   │   Results   │
   │   & Logs    │
   └─────────────┘
```

---

## 🔧 Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                    databricks.yml (DAB Config)                  │
│                                                                 │
│  bundle:                                                        │
│    name: "data_pipeline"                                        │
│                                                                 │
│  targets:                      ┌──────────────────────┐         │
│    dev_feature:                │  Controls:           │         │
│      workspace:                │  • Where to deploy   │         │
│        root_path: /Shared/...  │  • How to build      │         │
│                                │  • What to create    │         │
│      artifacts:                │  • Job configuration │         │
│        type: whl               └──────────────────────┘         │
│        build: python setup.py                                   │
│                                                                 │
│      resources:                                                 │
│        jobs:                                                    │
│          data_pipeline-...:                                     │
│            tasks: [...]                                         │
│            job_clusters: [...]                                  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Reads configuration
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              Databricks CLI (Unified v0.272.0+)                 │
│                                                                 │
│  Commands:                     ┌──────────────────────┐         │
│  • bundle validate             │  Actions:            │         │
│  • bundle deploy               │  • Parse YAML        │         │
│  • bundle run                  │  • Call APIs         │         │
│                                │  • Upload files      │         │
│  Authentication:               │  • Create resources  │         │
│  • Host: from secrets          └──────────────────────┘         │
│  • Token: from secrets                                          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ API Calls
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Databricks REST API                          │
│                                                                 │
│  Endpoints:                    ┌──────────────────────┐         │
│  • /api/2.0/workspace/...      │  Operations:         │         │
│  • /api/2.1/jobs/...           │  • Upload artifacts  │         │
│  • /api/2.0/clusters/...       │  • Create jobs       │         │
│                                │  • Run jobs          │         │
│                                │  • Get status        │         │
│                                └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Fix Implementation Map

```
┌────────────────────────────────────────────────────────────────┐
│                         FIX #1                                 │
│          CLI Installation & PATH Management                    │
│                                                                │
│  Problem: databricks: command not found                       │
│                                                                │
│  Solution:                                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 1. Use official installation script                     │ │
│  │    curl -fsSL .../install.sh | sh                       │ │
│  │                                                          │ │
│  │ 2. Add to $GITHUB_PATH (persists)                       │ │
│  │    echo "/usr/local/bin" >> $GITHUB_PATH                │ │
│  │                                                          │ │
│  │ 3. Use databricks configure --token                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                         FIX #2                                 │
│            Configuration Format Conflicts                      │
│                                                                │
│  Problem: both 'environments' and 'targets' specified          │
│                                                                │
│  Solution:                                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 1. Remove include directive from databricks.yml         │ │
│  │    ❌ include: - "deployment_conf/**/*.yml"             │ │
│  │                                                          │ │
│  │ 2. Deprecate old deployment files                       │ │
│  │    Comment out rep_smoke_deployment_dev_feature_val.yml │ │
│  │                                                          │ │
│  │ 3. Use only 'targets' in databricks.yml                │ │
│  │    ✅ targets: dev_feature: ...                         │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                         FIX #3                                 │
│           Multiple CLI Versions Conflict                       │
│                                                                │
│  Problem: v0.17.8 vs v0.272.0 both installed                   │
│                                                                │
│  Solution:                                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 1. Remove legacy CLI explicitly                         │ │
│  │    pip uninstall -y databricks-cli databricks           │ │
│  │                                                          │ │
│  │ 2. Prepend /usr/local/bin to PATH                       │ │
│  │    (ensures new CLI is found first)                     │ │
│  │                                                          │ │
│  │ 3. Set environment variable globally                    │ │
│  │    DATABRICKS_CLI_DO_NOT_EXECUTE_NEWER_VERSION=1        │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

**Created:** October 10, 2025  
**Purpose:** Visual reference for the complete CI/CD architecture  
**Audience:** Development team, DevOps engineers
