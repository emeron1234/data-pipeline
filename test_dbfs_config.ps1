# PowerShell script to test DBFS configuration for Windows users
# Run this to verify your configuration before deploying

Write-Host "=== DBFS Configuration Test ===" -ForegroundColor Cyan

Write-Host ""
Write-Host "1. Checking current .dbx/project.json configuration:" -ForegroundColor Yellow

if (Test-Path ".dbx/project.json") {
    $content = Get-Content ".dbx/project.json" | Out-String
    Write-Host $content
    
    # Check for required fields
    $requiredFields = @("workspace_dir", "artifact_location")
    $missingFields = @()
    
    foreach ($field in $requiredFields) {
        if (-not ($content -match "`"$field`"")) {
            $missingFields += $field
        }
    }
    
    if ($missingFields.Count -eq 0) {
        Write-Host "✅ All required fields present" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing required fields: $($missingFields -join ', ')" -ForegroundColor Red
        Write-Host "💡 This will cause validation errors" -ForegroundColor Yellow
    }
    
    # Check artifact location
    if ($content -match '"artifact_location".*"dbfs:/') {
        $artifactLocation = ($content | Select-String '"artifact_location".*"(dbfs:[^"]*)"' | ForEach-Object { $_.Matches[0].Groups[1].Value }) | Select-Object -First 1
        Write-Host "📍 Found artifact_location: $artifactLocation" -ForegroundColor Cyan
        
        if ($artifactLocation -match "dbfs:/dbx/.*" -or $artifactLocation -match "dbfs:/mnt/.*") {
            Write-Host "❌ WARNING: This may cause DBFS root access issues!" -ForegroundColor Red
            Write-Host "💡 Consider using FileStore or tmp directory instead." -ForegroundColor Yellow
        } elseif ($artifactLocation -match "dbfs:/tmp/.*" -or $artifactLocation -match "dbfs:/FileStore/.*" -or $artifactLocation -match "dbfs:/Users/.*") {
            Write-Host "✅ Artifact location should be compatible with Free Edition." -ForegroundColor Green
        } else {
            Write-Host "⚠️  Unknown artifact location - test in your workspace first." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ No artifact_location found - this will cause validation errors" -ForegroundColor Red
    }
} else {
    Write-Host "❌ .dbx/project.json not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. Checking available configuration variants:" -ForegroundColor Yellow

$configs = @{
    ".dbx/project_free_edition.json" = "Free Edition (tmp directory)"
    ".dbx/project_filestore.json" = "FileStore (recommended for Free Edition)"
    ".dbx/project_user_specific.json" = "User-specific paths"
}

foreach ($configFile in $configs.Keys) {
    $configDesc = $configs[$configFile]
    
    if (Test-Path $configFile) {
        Write-Host "✅ $configDesc exists" -ForegroundColor Green
        
        $configContent = Get-Content $configFile | Out-String
        $requiredFields = @("workspace_dir", "artifact_location")
        $missingFields = @()
        
        foreach ($field in $requiredFields) {
            if (-not ($configContent -match "`"$field`"")) {
                $missingFields += $field
            }
        }
        
        if ($missingFields.Count -eq 0) {
            Write-Host "   ✅ All required fields present" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Missing fields: $($missingFields -join ', ')" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ $configDesc not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "3. Testing deployment configuration:" -ForegroundColor Yellow

$deploymentFile = "deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml"
if (Test-Path $deploymentFile) {
    Write-Host "✅ Free Edition deployment config exists" -ForegroundColor Green
    
    $deployContent = Get-Content $deploymentFile | Out-String
    
    # Check for problematic configurations
    if ($deployContent -match "policy_id") {
        Write-Host "⚠️  Found policy_id in Free Edition config - this may cause issues" -ForegroundColor Yellow
    }
    
    if ($deployContent -match "autoscale") {
        Write-Host "⚠️  Found autoscale in Free Edition config - this may cause issues" -ForegroundColor Yellow
    }
    
    if ($deployContent -match "num_workers: 0") {
        Write-Host "✅ Single-node cluster configuration found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Single-node cluster (num_workers: 0) not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Free Edition deployment config not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Quick fix commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use FileStore config (recommended for Free Edition):" -ForegroundColor Cyan
Write-Host "  Copy-Item .dbx/project_filestore.json .dbx/project.json" -ForegroundColor White
Write-Host ""
Write-Host "To use tmp directory config:" -ForegroundColor Cyan
Write-Host "  Copy-Item .dbx/project_free_edition.json .dbx/project.json" -ForegroundColor White
Write-Host ""
Write-Host "To use user-specific config:" -ForegroundColor Cyan
Write-Host "  Copy-Item .dbx/project_user_specific.json .dbx/project.json" -ForegroundColor White
Write-Host "  # Note: Replace `${USER} with your actual username" -ForegroundColor Gray
Write-Host ""
Write-Host "To validate dbx configuration:" -ForegroundColor Cyan
Write-Host "  dbx configure --profile DEFAULT --environment dev_feature" -ForegroundColor White
Write-Host ""
Write-Host "To test deployment (dry run):" -ForegroundColor Cyan
Write-Host "  dbx deploy --dry-run --job=we-pipeline-rep-smoke-dev-feature-val-v1 ``" -ForegroundColor White
Write-Host "    --deployment-file=deployment_conf/validation/rep_smoke_deployment_dev_feature_val_free_edition.yml ``" -ForegroundColor White
Write-Host "    --environment dev_feature" -ForegroundColor White

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host "✅ If no errors above, configuration should work with Free Edition" -ForegroundColor Green
Write-Host "📖 See DBFS_TROUBLESHOOTING.md for detailed troubleshooting" -ForegroundColor Cyan