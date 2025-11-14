# Data Pipeline - Databricks Asset Bundle (DAB) Project

The project demonstrates end-to-end expertise in ETL pipeline development, data quality validation and CI/CD automation which, deployed using **Databricks Asset Bundles (DAB)** for modern CI/CD practices.

### **Business Requirement** ###
Engineered a scalable data pipeline processing **Contact Information** and **Real Estate** datasets through a multi-layer architecture, ensuring data quality, compliance, and production readiness for enterprise analytics.

---

## 🚀 Quick Start

### **Project Highlights**
- Pipeline Architecture implementation
    - Bronze → Silver → Gold
- Automated CI/CD pipeline
    - using GithHub Action
- QA Framework
    - Smoke and Regression testing
- Modern Deployment
    - using Databricks Asset Bundles (DAB)
- Data Quality validation
    - performed at every stage of task run

### **CI/CD Deployment**
The GitHub Actions workflow automatically:
1. ✅ Installs correct Databricks CLI
2. ✅ Validates bundle configuration
3. ✅ Deploys to Databricks workspace
4. ✅ Runs validation jobs

---

## 📋 Project Structure

```
data-pipeline/
├── .github/workflows/
│   └── qa_val.yml              # CI/CD workflow (DAB-based)
├── data_pipeline/              # Application code
│   ├── core/
│   ├── real_estate/
│   └── validation/
├── databricks.yml              # DAB configuration (MAIN)
└── setup.py                    # Python package setup
```

┌────────────────────────────────────────────────────────────────────┐
│                      DATA ENGINEERING PIPELINE                     │
└────────────────────────────────────────────────────────────────────┘
```
📁 Data Sources                  🔄 Processing Layers              📊 Analytics
     │                                   │                             │
     ├─► Synthetic Data ────────► 🟦 Raw Zone ──────────────────────► │
     │   Generator                  │ (Parquet Files)                 │
     │   (Faker)                    │ - No transformation             │
     │                              │ - Batch tracking                │
     │                              │                                 │
     │                              ▼                                 │
     │                         🟧 Bronze Zone ──────────────────────► │
     │                              │ - Data cleansing                │
     │                              │ - Null filtering                │
     │                              │ - Special char removal          │
     │                              │ - Phone standardization         │
     │                              │ - Name normalization            │
     │                              │                                 │
     │                              ▼                                 │
     │                         🟨 Silver Zone ──────────────────────► │
     │                              │ - Delta Lake tables             │
     │                              │ - Schema evolution              │
     │                              │ - ACID transactions             │
     │                              │ - Ready for analytics           │
     │                              │                                 │
     │                              ▼                                 │
     │                         🟩 Gold Zone (Planned) ──────────────► │
     │                                - Aggregations                  │
     │                                - Business metrics              │
     │                                - Feature engineering           │
     │                                                                 │
     └────────────────────────────────────────────────────────────────┘
```
                    ✅ Validation Layer (Parallel)
                         │
                         ├─► Smoke Tests (Fast)
                         │   - Schema validation
                         │   - Row count checks
                         │   - Critical column checks
                         │
                         └─► Regression Tests (Comprehensive)
                             - Data comparison
                             - Business rule validation
                             - Historical consistency

---

## 🔧 Key Technologies

- **Deployment**: Databricks Asset Bundles (DAB)
- **CI/CD**: GitHub Actions
- **Language**: Python 3.9+
- **Build**: setuptools (wheel packages)
- **Orchestration**: Databricks Workflows

---
