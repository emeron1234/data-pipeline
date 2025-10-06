#!/bin/bash

# Databricks Free Edition Setup Script
# This script helps you set up the environment for running jobs on Databricks Free Edition

echo "=== Databricks Free Edition Setup ==="

echo "1. First, ensure you have the following GitHub Secrets configured:"
echo "   - DATABRICKS_HOST: Your Databricks workspace URL (e.g., https://community.cloud.databricks.com)"
echo "   - DATABRICKS_TOKEN: Personal access token from Databricks"
echo "   - GH_TOKEN: GitHub personal access token"

echo ""
echo "2. To get your Databricks token:"
echo "   - Log into your Databricks workspace"
echo "   - Click on your profile (top right)"
echo "   - Go to 'User Settings'"
echo "   - Click 'Access tokens'"
echo "   - Generate new token"

echo ""
echo "3. Available cluster configurations for Free Edition:"
echo "   Check your Databricks workspace for available node types:"
echo "   - Go to Compute → Create Compute"
echo "   - See available node types (usually i3.xlarge or similar)"

echo ""
echo "4. File paths to update for Free Edition:"
echo "   - Remove policy_id from cluster configuration"
echo "   - Use num_workers: 0 for single-node cluster"
echo "   - Remove Unity Catalog configurations"
echo "   - Remove access control lists"

echo ""
echo "5. To trigger the workflow:"
echo "   Method 1 - GitHub UI:"
echo "   - Go to Actions tab in GitHub"
echo "   - Select 'QA Validation Workflow Deployment'"
echo "   - Click 'Run workflow'"
echo "   - Set parameters:"
echo "     Environment: dev"
echo "     Space: feature"
echo "     Object type: re"
echo "     Job type: rep"
echo "     Test type: smoke"
echo "     Deploy: true"

echo ""
echo "6. To use the Free Edition compatible deployment file:"
echo "   Update qa_workflow.yml to use:"
echo "   deployment_file: ./deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml"

echo ""
echo "Setup complete! Check the DEPLOYMENT_GUIDE.md for detailed instructions."