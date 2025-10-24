# Test Render deployment
# Replace YOUR_APP_URL with your actual Render URL

$BASE_URL = "https://secure-chat-app-xxxx.onrender.com"  # UPDATE THIS

Write-Host "Testing Render Deployment..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Test 1: Root endpoint
Write-Host "`n1. Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
    Write-Host "✅ Root endpoint working!" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Root endpoint failed: $_" -ForegroundColor Red
}

# Test 2: Security status
Write-Host "`n2. Testing security status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/security/status" -Method Get
    Write-Host "✅ Security status working!" -ForegroundColor Green
    Write-Host "ML Detection Enabled: $($response.ml_phishing_detection.enabled)" -ForegroundColor Cyan
    Write-Host "Python Version Used: Check logs" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Security status failed: $_" -ForegroundColor Red
}

# Test 3: Static files
Write-Host "`n3. Testing static files..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/static/index.html" -Method Get
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Static files working!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Static files failed: $_" -ForegroundColor Red
}

# Test 4: Signup endpoint
Write-Host "`n4. Testing signup endpoint..." -ForegroundColor Yellow
$testUser = @{
    email = "test@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/signup" -Method Post -Body $testUser -ContentType "application/json"
    Write-Host "✅ Signup endpoint working!" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✅ Signup endpoint working (user may already exist)" -ForegroundColor Green
    } else {
        Write-Host "❌ Signup failed: $_" -ForegroundColor Red
    }
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Testing complete!" -ForegroundColor Cyan
Write-Host "`nYour app URL: $BASE_URL" -ForegroundColor Green
Write-Host "Frontend: $BASE_URL/static/index.html" -ForegroundColor Green
