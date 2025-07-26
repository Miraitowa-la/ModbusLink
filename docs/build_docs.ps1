# PowerShell script to build ModbusLink documentation
# This script builds both English and Chinese versions of the documentation

Write-Host "Building ModbusLink Documentation" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Get the docs directory
$DocsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildDir = Join-Path $DocsDir "_build\html"

# Clean build directory
if (Test-Path $BuildDir) {
    Write-Host "Cleaning build directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $BuildDir
}

# Create build directory
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

# Build English documentation
Write-Host "`nBuilding English documentation..." -ForegroundColor Cyan
$EnBuildDir = Join-Path $BuildDir "en"
try {
    & sphinx-build -b html -c (Join-Path $DocsDir "en") (Join-Path $DocsDir "en") $EnBuildDir
    if ($LASTEXITCODE -ne 0) {
        throw "English documentation build failed"
    }
    Write-Host "English documentation built successfully" -ForegroundColor Green
} catch {
    Write-Host "Error building English documentation: $_" -ForegroundColor Red
    exit 1
}

# Build Chinese documentation
Write-Host "`nBuilding Chinese documentation..." -ForegroundColor Cyan
$ZhBuildDir = Join-Path $BuildDir "zh"
try {
    & sphinx-build -b html -c (Join-Path $DocsDir "zh") (Join-Path $DocsDir "zh") $ZhBuildDir
    if ($LASTEXITCODE -ne 0) {
        throw "Chinese documentation build failed"
    }
    Write-Host "Chinese documentation built successfully" -ForegroundColor Green
} catch {
    Write-Host "Error building Chinese documentation: $_" -ForegroundColor Red
    exit 1
}

# Create main index page
Write-Host "`nCreating main index page..." -ForegroundColor Cyan
$IndexContent = @'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModbusLink Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: #f8f9fa;
        }
        .container {
            background: white;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 2rem;
        }
        .language-selector {
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-top: 2rem;
        }
        .language-card {
            background: #3498db;
            color: white;
            padding: 2rem;
            border-radius: 8px;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            min-width: 200px;
        }
        .language-card:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        .language-card h2 {
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
        }
        .language-card p {
            margin: 0;
            opacity: 0.9;
        }
        .description {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .build-info {
            text-align: center;
            color: #95a5a6;
            font-size: 0.9rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #ecf0f1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ModbusLink Documentation</h1>
        <p class="description">
            Welcome to ModbusLink documentation. Choose your preferred language to get started.
            <br>
            欢迎使用ModbusLink文档。请选择您的首选语言开始使用。
        </p>
        <div class="language-selector">
            <a href="en/index.html" class="language-card">
                <h2>English</h2>
                <p>English Documentation</p>
            </a>
            <a href="zh/index.html" class="language-card">
                <h2>中文</h2>
                <p>中文文档</p>
            </a>
        </div>
        <div class="build-info">
            Built with Sphinx • ModbusLink Documentation
        </div>
    </div>
</body>
</html>
'@

$IndexPath = Join-Path $BuildDir "index.html"
$IndexContent | Out-File -FilePath $IndexPath -Encoding UTF8
Write-Host "Created index page: $IndexPath" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Documentation build completed!" -ForegroundColor Green
Write-Host "Output directory: $BuildDir" -ForegroundColor Yellow
Write-Host "Open $IndexPath in your browser to view the documentation." -ForegroundColor Yellow

# Optionally open the documentation in the default browser
$OpenBrowser = Read-Host "`nWould you like to open the documentation in your browser? (y/N)"
if ($OpenBrowser -eq 'y' -or $OpenBrowser -eq 'Y') {
    Start-Process $IndexPath
}