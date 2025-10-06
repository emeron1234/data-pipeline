#!/bin/bash

# Quick test script for DBFS configuration
# Run this to verify your configuration before deploying

echo "=== DBFS Configuration Test ==="

echo ""
echo "1. Checking current .dbx/project.json configuration:"
if [ -f ".dbx/project.json" ]; then
    cat .dbx/project.json
    echo ""
    
    # Check if artifact_location contains dbfs root paths
    if grep -q '"artifact_location".*"dbfs:/' .dbx/project.json; then
        artifact_location=$(grep '"artifact_location"' .dbx/project.json | cut -d'"' -f4)
        echo "⚠️  Found artifact_location: $artifact_location"
        
        if [[ "$artifact_location" == dbfs:/dbx/* ]] || [[ "$artifact_location" == dbfs:/mnt/* ]]; then
            echo "❌ WARNING: This may cause DBFS root access issues!"
            echo "💡 Consider using the Free Edition config instead."
        else
            echo "✅ Artifact location should be compatible."
        fi
    else
        echo "✅ No artifact_location specified - will use MLflow default (recommended)"
    fi
else
    echo "❌ .dbx/project.json not found!"
fi

echo ""
echo "2. Checking Free Edition configuration:"
if [ -f ".dbx/project_free_edition.json" ]; then
    echo "✅ Free Edition config exists:"
    cat .dbx/project_free_edition.json
else
    echo "❌ Free Edition config not found - creating it now..."
    mkdir -p .dbx
    cat > .dbx/project_free_edition.json << 'EOF'
{
    "environments": {
        "dev_feature": {
            "profile": "DEFAULT",
            "properties": {
                "workspace_directory": "/Users/shared/dbx/projects/we-pipeline_dev_feature"
            }
        }
    }
}
EOF
    echo "✅ Created .dbx/project_free_edition.json"
fi

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
echo "To use Free Edition config:"
echo "  cp .dbx/project_free_edition.json .dbx/project.json"
echo ""
echo "To test deployment (dry run):"
echo "  dbx deploy --dry-run --job=we-pipeline-rep-smoke-dev-feature-val-v1 \\"
echo "    --deployment-file=deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml \\"
echo "    --environment dev_feature"

echo ""
echo "=== Test Complete ==="
echo "✅ If no errors above, configuration should work with Free Edition"
echo "📖 See DBFS_TROUBLESHOOTING.md for detailed troubleshooting"