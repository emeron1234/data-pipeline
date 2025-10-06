#!/bin/bash

# Quick test script for DBFS configuration
# Run this to verify your configuration before deploying

echo "=== DBFS Configuration Test ==="

echo ""
echo "1. Checking current .dbx/project.json configuration:"
if [ -f ".dbx/project.json" ]; then
    cat .dbx/project.json
    echo ""
    
    # Check for required fields
    required_fields=("workspace_dir" "artifact_location")
    missing_fields=()
    
    for field in "${required_fields[@]}"; do
        if ! grep -q "\"$field\"" .dbx/project.json; then
            missing_fields+=("$field")
        fi
    done
    
    if [ ${#missing_fields[@]} -eq 0 ]; then
        echo "✅ All required fields present"
    else
        echo "❌ Missing required fields: ${missing_fields[*]}"
        echo "💡 This will cause validation errors"
    fi
    
    # Check if artifact_location contains dbfs root paths
    if grep -q '"artifact_location".*"dbfs:/' .dbx/project.json; then
        artifact_location=$(grep '"artifact_location"' .dbx/project.json | head -1 | cut -d'"' -f4)
        echo "📍 Found artifact_location: $artifact_location"
        
        if [[ "$artifact_location" == dbfs:/dbx/* ]] || [[ "$artifact_location" == dbfs:/mnt/* ]]; then
            echo "❌ WARNING: This may cause DBFS root access issues!"
            echo "💡 Consider using FileStore or tmp directory instead."
        elif [[ "$artifact_location" == dbfs:/tmp/* ]] || [[ "$artifact_location" == dbfs:/FileStore/* ]] || [[ "$artifact_location" == dbfs:/Users/* ]]; then
            echo "✅ Artifact location should be compatible with Free Edition."
        else
            echo "⚠️  Unknown artifact location - test in your workspace first."
        fi
    else
        echo "❌ No artifact_location found - this will cause validation errors"
    fi
else
    echo "❌ .dbx/project.json not found!"
fi

echo ""
echo "2. Checking available configuration variants:"

configs=(
    ".dbx/project_free_edition.json:Free Edition (tmp directory)"
    ".dbx/project_filestore.json:FileStore (recommended for Free Edition)"
    ".dbx/project_user_specific.json:User-specific paths"
)

for config_info in "${configs[@]}"; do
    config_file=$(echo "$config_info" | cut -d':' -f1)
    config_desc=$(echo "$config_info" | cut -d':' -f2)
    
    if [ -f "$config_file" ]; then
        echo "✅ $config_desc exists"
        
        # Validate required fields
        required_fields=("workspace_dir" "artifact_location")
        missing_fields=()
        
        for field in "${required_fields[@]}"; do
            if ! grep -q "\"$field\"" "$config_file"; then
                missing_fields+=("$field")
            fi
        done
        
        if [ ${#missing_fields[@]} -eq 0 ]; then
            echo "   ✅ All required fields present"
        else
            echo "   ❌ Missing fields: ${missing_fields[*]}"
        fi
    else
        echo "❌ $config_desc not found"
    fi
done

echo ""
echo "3. Testing deployment configuration:"
if [ -f "deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml" ]; then
    echo "✅ Free Edition deployment config exists"
    
    # Check for problematic configurations
    if grep -q "policy_id" deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml; then
        echo "⚠️  Found policy_id in Free Edition config - this may cause issues"
    fi
    
    if grep -q "autoscale" deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml; then
        echo "⚠️  Found autoscale in Free Edition config - this may cause issues"
    fi
    
    if grep -q "num_workers: 0" deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml; then
        echo "✅ Single-node cluster configuration found"
    else
        echo "⚠️  Single-node cluster (num_workers: 0) not found"
    fi
    
else
    echo "❌ Free Edition deployment config not found!"
fi

echo ""
echo "4. Quick fix commands:"
echo ""
echo "To use FileStore config (recommended for Free Edition):"
echo "  cp .dbx/project_filestore.json .dbx/project.json"
echo ""
echo "To use tmp directory config:"
echo "  cp .dbx/project_free_edition.json .dbx/project.json"
echo ""
echo "To use user-specific config:"
echo "  cp .dbx/project_user_specific.json .dbx/project.json"
echo "  # Note: Replace \${USER} with your actual username"
echo ""
echo "To validate dbx configuration:"
echo "  dbx configure --profile DEFAULT --environment dev_feature"
echo ""
echo "To test deployment (dry run):"
echo "  dbx deploy --dry-run --job=we-pipeline-rep-smoke-dev-feature-val-v1 \\"
echo "    --deployment-file=deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml \\"
echo "    --environment dev_feature"

echo ""
echo "=== Test Complete ==="
echo "✅ If no errors above, configuration should work with Free Edition"
echo "📖 See DBFS_TROUBLESHOOTING.md for detailed troubleshooting"