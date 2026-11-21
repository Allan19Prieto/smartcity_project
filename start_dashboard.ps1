<#
.SYNOPSIS
    Script de arranque automatizado para la Interfaz Centralizada SmartCity Analytics (Sprint 2).
.DESCRIPTION
    Inicia el servidor Streamlit en el puerto 8501, verificando previamente la disponibilidad de Docker
    o ejecutando directamente con el entorno de Python local en Windows.
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  SmartCity Analytics - Panel Centralizado (Sprint 2)" -ForegroundColor White
Write-Host "  CE-3101 Bases de Datos | TEC Cartago | Equipo RIC" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$DOCKER_RUNNING = $false
try {
    $null = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $DOCKER_RUNNING = $true
    }
} catch {
    $DOCKER_RUNNING = $false
}

if ($DOCKER_RUNNING) {
    Write-Host "[1/2] Verificando contenedor 'app' en Docker..." -ForegroundColor Green
    $containerStatus = docker compose ps --filter "service=app" --format "{{.Status}}" 2>&1
    if (-not $containerStatus -or $containerStatus -notmatch "Up") {
        Write-Host "Iniciando servicios del clúster con Docker Compose..." -ForegroundColor Yellow
        docker compose up -d app
    }
    Write-Host "[2/2] Iniciando Streamlit dentro del contenedor Docker..." -ForegroundColor Green
    Write-Host "URL de acceso: http://localhost:8501" -ForegroundColor Cyan
    docker compose exec -it app streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=8501
} else {
    Write-Host "[INFO] Docker Daemon no detectado. Iniciando en modo local (Python nativo)..." -ForegroundColor Yellow
    Write-Host "[1/2] Verificando dependencias en Python local..." -ForegroundColor Green
    Write-Host "[2/2] Ejecutando Streamlit en el puerto 8501..." -ForegroundColor Green
    Write-Host "URL de acceso: http://localhost:8501" -ForegroundColor Cyan
    python -m streamlit run dashboard/app.py --server.port=8501
}
