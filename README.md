# Data Pipeline - Databricks Asset Bundle (DAB) Project

The project demonstrates end-to-end expertise in ETL pipeline development, data quality validation and CI/CD automation which, deployed using **Databricks Asset Bundles (DAB)** for modern CI/CD practices.

### **Business Requirement** ###
Engineered a scalable data pipeline processing **Contact Information** and **Real Estate** datasets through a multi-layer architecture, ensuring data quality, compliance, and production readiness for enterprise analytics.

---

## 🚀 Quick Start

### **Project Highlights**
- Pipeline Architecture implementation: Bronze → Silver → Gold
- Automated CI/CD pipeline: using GithHub Action
- QA Framework: Smoke and Regression testing
- Modern Deployment: using Databricks Asset Bundles (DAB)
- Data Quality validation: performed at every stage of task run

### **CI/CD Deployment**
The GitHub Actions workflow automatically:
1. ✅ Installs correct Databricks CLI
2. ✅ Validates bundle configuration
3. ✅ Deploys to Databricks workspace
4. ✅ Runs validation jobs

---

## 📋 Repository File Structure

```
data-pipeline/
├── .github/workflows/
│   └── data_etl.yml            # CI/CD workflow (DAB-based)
├── data_pipeline/              # Core application code
│   ├── contact_info/
│   ├── core/
│   ├── data_generation/
│   ├── real_estate/
│   └── validation/
├── databricks.yml              # DAB configuration (MAIN)
└── setup.py                    # Python package setup
```

---

## 🏗️ End-to-End Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                      DATA ENGINEERING PIPELINE                     │
└────────────────────────────────────────────────────────────────────┘

📁 Data Sources                  🔄 Processing Layers              📊 Analytics
     │                                   │                             │
     ├─► Synthetic Data ────────► 🟦 Raw Zone ──────────────────────► │
     │   Generator                  │ (Parquet Files)                  │
     │   (Faker)                    │ - No transformation              │
     │                              │ - Batch tracking                 │
     │                              │                                  │
     │                              ▼                                  │
     │                         🟧 Bronze Zone ──────────────────────► │
     │                              │ - Data cleansing                 │
     │                              │ - Null filtering                 │
     │                              │ - Special char removal           │
     │                              │ - Phone standardization          │
     │                              │ - Name normalization             │
     │                              │                                  │
     │                              ▼                                  │
     │                         🟨 Silver Zone ──────────────────────► │
     │                              │ - Delta Lake tables              │
     │                              │ - Schema evolution               │
     │                              │ - Ready for analytics            │
     │                              │                                  │
     │                              │                                  │
     │                              ▼                                  │
     │                         🟩 Gold Zone (Future Planned) ───────► │
     │                                - Aggregations                   │
     │                                - Business metrics               │
     │                                - Feature engineering            │
     │                                                                 │
     └─────────────────────────────────────────────────────────────────┘

                    ✅ Validation Layer (Parallel)
                         │
                         ├─► Smoke Tests (Fast)
                         │   - Business rule validation (YAML-based queries)
                         │   
                         └─► Regression Tests (Comprehensive)
                             - Schema validation
                             - Row count checks
                             - Data comparison
```
                             
---

## 🔧 Key End-to-End Pipeline

### ***Data Generation Module***
Built synthetic test data for development and testing:
```
# File: data_pipeline/data_generation/task/generate_data_task.py
def etl_process(**options):
    """Generate realistic synthetic data using Faker"""
    fake = Faker()
    
    # Intelligent batch ID management
    batch_id = batch_ids_processing(path)  # Auto-increments from last batch
    
    # Generate records with realistic patterns
    for i in range(num_rows):
        data.append({
            "profile_id": fake.uuid4(),
            "first_name": random_cases(fake.first_name()),
            "phone_personal": fake.phone_number(),
            # ... 20+ fields with realistic data
        })
```

---
