# Render Deployment Script for Windows PowerShell
# This script automates the Git setup and push process

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🚀 Render Deployment Script - Secure Chat App" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if we're in the correct directory
$currentDir = Get-Location
if (-not (Test-Path "server/main.py")) {
    Write-Host "❌ Error: Not in the correct directory!" -ForegroundColor Red
    Write-Host "   Please run this script from the cyberproject folder" -ForegroundColor Yellow
    Write-Host "   Current directory: $currentDir" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Current directory: $currentDir" -ForegroundColor Green
Write-Host ""

# Check if required files exist
Write-Host "🔍 Checking deployment files..." -ForegroundColor Yellow
$requiredFiles = @("Procfile", "render.yaml", "runtime.txt", ".gitignore", "server/requirements.txt", "server/main.py")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (missing)" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Missing required files. Please create them first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "📝 Git Configuration" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Check if Git is already initialized
if (Test-Path ".git") {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
    
    # Check if there are uncommitted changes
    $status = git status --porcelain
    if ($status) {
        Write-Host "⚠️  You have uncommitted changes" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Would you like to commit these changes? (Y/N)" -ForegroundColor Yellow
        $commit = Read-Host
        
        if ($commit -eq "Y" -or $commit -eq "y") {
            Write-Host ""
            Write-Host "Enter commit message:" -ForegroundColor Yellow
            $commitMessage = Read-Host
            
            Write-Host ""
            Write-Host "📦 Staging changes..." -ForegroundColor Yellow
            git add .
            
            Write-Host "💾 Committing changes..." -ForegroundColor Yellow
            git commit -m $commitMessage
            
            Write-Host "✅ Changes committed" -ForegroundColor Green
        }
    } else {
        Write-Host "✅ No uncommitted changes" -ForegroundColor Green
    }
} else {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
    Write-Host ""
    
    # Configure Git user
    Write-Host "Enter your Git username:" -ForegroundColor Yellow
    $gitUser = Read-Host
    git config user.name $gitUser
    
    Write-Host "Enter your Git email:" -ForegroundColor Yellow
    $gitEmail = Read-Host
    git config user.email $gitEmail
    
    Write-Host "✅ Git configured" -ForegroundColor Green
    Write-Host ""
    
    # Initial commit
    Write-Host "📦 Staging all files..." -ForegroundColor Yellow
    git add .
    
    Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
    git commit -m "Initial commit: Secure Chat App ready for Render deployment"
    
    Write-Host "✅ Initial commit created" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🌐 GitHub Setup" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Check if remote already exists
$remotes = git remote
if ($remotes -contains "origin") {
    Write-Host "✅ GitHub remote already configured" -ForegroundColor Green
    $remoteUrl = git remote get-url origin
    Write-Host "   Remote URL: $remoteUrl" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Would you like to push to GitHub? (Y/N)" -ForegroundColor Yellow
    $pushChoice = Read-Host
    
    if ($pushChoice -eq "Y" -or $pushChoice -eq "y") {
        Write-Host ""
        Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
        
        try {
            git push origin main
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Push failed. Trying to set upstream..." -ForegroundColor Yellow
            git push -u origin main
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
        }
    }
} else {
    Write-Host "⚠️  No GitHub remote configured" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Have you created a GitHub repository? (Y/N)" -ForegroundColor Yellow
    $hasRepo = Read-Host
    
    if ($hasRepo -eq "Y" -or $hasRepo -eq "y") {
        Write-Host ""
        Write-Host "Enter your GitHub username:" -ForegroundColor Yellow
        $githubUser = Read-Host
        
        Write-Host "Enter your repository name (e.g., secure-chat-app):" -ForegroundColor Yellow
        $repoName = Read-Host
        
        $repoUrl = "https://github.com/$githubUser/$repoName.git"
        
        Write-Host ""
        Write-Host "🔗 Adding GitHub remote..." -ForegroundColor Yellow
        git remote add origin $repoUrl
        
        Write-Host "✅ Remote added: $repoUrl" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
        git branch -M main
        
        try {
            git push -u origin main
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
        } catch {
            Write-Host "❌ Push failed. Please check:" -ForegroundColor Red
            Write-Host "   1. Repository exists on GitHub" -ForegroundColor Yellow
            Write-Host "   2. You have access to the repository" -ForegroundColor Yellow
            Write-Host "   3. GitHub credentials are correct" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "You can manually push later with: git push -u origin main" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "📝 Please create a GitHub repository first:" -ForegroundColor Yellow
        Write-Host "   1. Go to https://github.com/new" -ForegroundColor Cyan
        Write-Host "   2. Create a new repository (e.g., 'secure-chat-app')" -ForegroundColor Cyan
        Write-Host "   3. Make it PUBLIC (required for Render free tier)" -ForegroundColor Cyan
        Write-Host "   4. Do NOT initialize with README, .gitignore, or license" -ForegroundColor Cyan
        Write-Host "   5. Run this script again" -ForegroundColor Cyan
        Write-Host ""
        exit 0
    }
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🎯 Next Steps" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Git setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps to deploy on Render:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Go to https://dashboard.render.com" -ForegroundColor Cyan
Write-Host "2️⃣  Click 'New +' → 'Web Service'" -ForegroundColor Cyan
Write-Host "3️⃣  Connect your GitHub repository" -ForegroundColor Cyan
Write-Host "4️⃣  Configure the service:" -ForegroundColor Cyan
Write-Host "     • Name: secure-chat-app" -ForegroundColor White
Write-Host "     • Runtime: Python 3" -ForegroundColor White
Write-Host "     • Build Command: pip install -r server/requirements.txt" -ForegroundColor White
Write-Host "     • Start Command: cd server && uvicorn main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor White
Write-Host "5️⃣  Add environment variables (see .env.example)" -ForegroundColor Cyan
Write-Host "6️⃣  Click 'Create Web Service'" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔐 IMPORTANT: Set these environment variables in Render:" -ForegroundColor Red
Write-Host "   • SECRET_KEY (generate random 64+ characters)" -ForegroundColor Yellow
Write-Host "   • AES_SECRET_KEY (generate random 32 characters)" -ForegroundColor Yellow
Write-Host "   • AES_IV (generate random 16 characters)" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Generate random keys with:" -ForegroundColor Cyan
Write-Host "   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]`$_})" -ForegroundColor White
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🎉 Ready to deploy!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to generate QR code
Write-Host "Would you like to generate a QR code for your deployment? (Y/N)" -ForegroundColor Yellow
Write-Host "(You'll need your Render URL first)" -ForegroundColor Gray
$generateQR = Read-Host

if ($generateQR -eq "Y" -or $generateQR -eq "y") {
    Write-Host ""
    Write-Host "📱 Launching QR code generator..." -ForegroundColor Yellow
    python generate_deployment_qr.py
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
