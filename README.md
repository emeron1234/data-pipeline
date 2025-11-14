# Data Pipeline - Databricks Asset Bundle (DAB) Project

The project demonstrates end-to-end expertise in ETL pipeline development, data quality validation and CI/CD automation which, deployed using **Databricks Asset Bundles (DAB)** for modern CI/CD practices.

---

## 🚀 Quick Start

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

---

## 🔧 Key Technologies

- **Deployment**: Databricks Asset Bundles (DAB)
- **CI/CD**: GitHub Actions
- **Language**: Python 3.9+
- **Build**: setuptools (wheel packages)
- **Orchestration**: Databricks Workflows

---
