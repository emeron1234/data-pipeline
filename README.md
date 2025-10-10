# Data Pipeline - Databricks Asset Bundle (DAB) Project

This package contains all the necessary classes and functions for the data engineering framework, deployed using **Databricks Asset Bundles (DAB)** for modern CI/CD practices.

---

## 📚 Documentation Index

### **Getting Started**
- 🚀 [Quick Reference](./QUICK_REFERENCE.md) - Common commands and quick start guide
- 🏗️ [CI/CD Architecture](./reference_files/CICD_ARCHITECTURE.md) - Complete architecture documentation

---

## 🚀 Quick Start

### **Local Development**
```bash
# 1. Build the wheel package
python setup.py bdist_wheel

# 2. Validate bundle configuration
databricks bundle validate -t dev_feature

# 3. Deploy to Databricks
databricks bundle deploy -t dev_feature

# 4. Run job
databricks bundle run -t dev_feature data_pipeline-rep-smoke-dev-feature-val-v1
```

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
├── setup.py                    # Python package setup
└── Documentation files         # See index above
```

---

## 🔧 Key Technologies

- **Deployment**: Databricks Asset Bundles (DAB)
- **CI/CD**: GitHub Actions
- **Language**: Python 3.9+
- **Build**: setuptools (wheel packages)
- **Orchestration**: Databricks Workflows

---

## ✨ Recent Updates (October 2025)

### **Migrated to Databricks Asset Bundles**
- ✅ Moved from legacy dbx to modern DAB approach
- ✅ Fixed CLI installation and PATH issues
- ✅ Resolved configuration format conflicts
- ✅ Eliminated multiple CLI version warnings

See [FINAL_SUMMARY.md](./reference_files/FINAL_SUMMARY.md) for complete details.

---

## 🤝 Contributing

When making changes:
1. Test in `dev_feature` environment first
2. Run `databricks bundle validate` before committing
3. Update documentation as needed
4. Create PR with detailed description

---

## 📞 Support

For issues or questions:
- Review documentation files listed above
- Check GitHub Actions logs
- Review Databricks job logs
- Contact DataVerse & DataAvengers Team

---