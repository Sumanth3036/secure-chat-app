# API Functionality Test Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧪 Testing CyberProject API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Server Health Check
Write-Host "Test 1: Server Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
    Write-Host "✅ PASS: Server is running" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAIL: Server not responding" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Favicon endpoint
Write-Host "Test 2: Favicon Endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/favicon.ico" -Method GET
    if ($response.StatusCode -eq 204) {
        Write-Host "✅ PASS: Favicon returns 204 No Content" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ FAIL: Favicon endpoint error" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Create Session
Write-Host "Test 3: Create Session" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/create_session" -Method POST
    Write-Host "✅ PASS: Session created" -ForegroundColor Green
    Write-Host "Session ID: $($response.session_id)" -ForegroundColor Gray
    Write-Host "Join URL: $($response.join_url)" -ForegroundColor Gray
    $global:sessionId = $response.session_id
} catch {
    Write-Host "❌ FAIL: Could not create session" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Signup
Write-Host "Test 4: User Signup" -ForegroundColor Yellow
$testEmail = "testuser_$(Get-Random)@example.com"
$testPassword = "SecurePass123!@#"
try {
    $body = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/signup" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ PASS: User signup successful" -ForegroundColor Green
    Write-Host "Response: $($response.message)" -ForegroundColor Gray
    $global:testEmail = $testEmail
    $global:testPassword = $testPassword
} catch {
    Write-Host "❌ FAIL: Signup failed" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: Login
Write-Host "Test 5: User Login" -ForegroundColor Yellow
try {
    $body = @{
        email = $global:testEmail
        password = $global:testPassword
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/login" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ PASS: Login successful" -ForegroundColor Green
    Write-Host "Token received: $($response.token.Substring(0, 20))..." -ForegroundColor Gray
    $global:authToken = $response.token
} catch {
    Write-Host "❌ FAIL: Login failed" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 6: Content Validation (Security)
Write-Host "Test 6: Security Validation API" -ForegroundColor Yellow
try {
    $body = @{
        content = "Click here to win FREE MONEY: http://phishing-site.com/login"
        session_id = "test-session-123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/validate" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ PASS: Validation API working" -ForegroundColor Green
    Write-Host "Is Threat: $($response.is_threat)" -ForegroundColor Gray
    Write-Host "Threat Score: $($response.threat_score)" -ForegroundColor Gray
    Write-Host "Detected Threats: $($response.threats -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAIL: Validation API error" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎯 Test Summary Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open browser: http://localhost:8000/static/signup.html" -ForegroundColor White
Write-Host "2. Create account and login" -ForegroundColor White
Write-Host "3. Test chat: http://localhost:8000/static/index.html" -ForegroundColor White
Write-Host "4. Test validation: http://localhost:8000/static/validate.html" -ForegroundColor White
Write-Host ""
