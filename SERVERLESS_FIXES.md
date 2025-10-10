# Serverless Compute Fixes

## Issue 1: PySpark Version Conflict ❌

### Error Message:
```
ModuleNotFoundError: No module named 'pyspark.sql.connect'
Library installation failed: Failed to restart Python
```

### Root Cause:
- `setup.py` included `pyspark==3.3.0` in `install_requires`
- Databricks serverless compute provides PySpark 3.5+ with `pyspark.sql.connect` module
- Installing an older PySpark version in the wheel caused runtime conflicts

### Solution:
✅ **Removed PySpark from wheel dependencies** in `setup.py`:
```python
PACKAGE_REQUIREMENTS = [
    'nameparser==1.1.2',
    # PySpark is provided by Databricks runtime - don't include in wheel
    # 'pyspark==3.3.0',
    'smartystreets_python_sdk==4.16.1',
    # ... other dependencies
]
```

✅ **Also removed `graphframes==0.6`** since it depends on PySpark

### Why This Works:
- Databricks serverless runtime already includes PySpark
- Your code uses the runtime-provided PySpark (compatible version)
- No version conflicts during library installation

---

## Issue 2: Missing Entry Point Module ❌

### Error Message:
```
ModuleNotFoundError: No module named 'data_pipeline.entry_point'
```

### Root Cause:
- `setup.py` defined entry point as `data_pipeline.entry_point:main`
- But `main.py` was in the root directory, not inside the `data_pipeline` package
- The module path didn't match the actual file structure

### Solution:
✅ **Moved and renamed the entry point file**:
```
main.py → data_pipeline/entry_point.py
```

✅ **Wrapped logic in a `main()` function**:
```python
def main():
    """Main entry point for the data pipeline ETL."""
    parser = argparse.ArgumentParser()
    # ... rest of the logic
    
if __name__ == '__main__':
    main()
```

### File Structure (Before):
```
data-pipeline/
├── main.py                    ❌ Not importable as data_pipeline.entry_point
├── setup.py
└── data_pipeline/
    ├── __init__.py
    ├── core/
    ├── real_estate/
    └── validation/
```

### File Structure (After):
```
data-pipeline/
├── setup.py
└── data_pipeline/
    ├── __init__.py
    ├── entry_point.py         ✅ Importable as data_pipeline.entry_point
    ├── core/
    ├── real_estate/
    └── validation/
```

---

## Summary of Changes

### Files Modified:
1. **`setup.py`**
   - Removed `pyspark==3.3.0` from `PACKAGE_REQUIREMENTS`
   - Removed `graphframes==0.6` from `PACKAGE_REQUIREMENTS`
   - Entry point definition remains: `data-pipeline-etl = data_pipeline.entry_point:main`

2. **`main.py` → `data_pipeline/entry_point.py`**
   - Moved file into the package
   - Wrapped main logic in `main()` function
   - Preserved all original functionality

### What Stays the Same:
- ✅ Entry point name: `data-pipeline-etl`
- ✅ Command-line interface and arguments
- ✅ All business logic and ETL processes
- ✅ `databricks.yml` configuration (no changes needed)

---

## Testing Steps

### 1. Rebuild the Wheel (GitHub Actions)
The workflow will automatically:
```bash
python setup.py bdist_wheel
```

### 2. Redeploy the Bundle
```bash
databricks bundle deploy -t dev_feature
```

### 3. Run the Job
```bash
databricks bundle run -t dev_feature data_pipeline-rep-smoke-dev-feature-val-v1
```

---

## Key Learnings

### ✅ DO:
- Let Databricks runtime provide PySpark
- Keep entry point files inside the package directory
- Use `main()` function wrapper for console scripts
- Exclude platform-provided libraries from wheel dependencies

### ❌ DON'T:
- Include PySpark in wheel for Databricks serverless
- Place entry point modules outside the package
- Use `if __name__ == '__main__':` as the only entry point definition

---

## Next Deployment

When you push these changes and run the GitHub Actions workflow:

1. ✅ Build step will create wheel without PySpark conflicts
2. ✅ Deploy step will upload the correct wheel
3. ✅ Job execution will find `data_pipeline.entry_point:main`
4. ✅ Python kernel will start without library conflicts

The job should now run successfully on serverless compute! 🚀
