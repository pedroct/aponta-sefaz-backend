# ===========================================
# Script de Desenvolvimento Local (PowerShell)
# Uso: .\scripts\dev.ps1 [start|stop|restart|status]
# ===========================================

param(
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "start"
)

$Port = 8000
$PidFile = ".dev.pid"

function Stop-DevServer {
    Write-Host "Parando servidor..." -ForegroundColor Yellow

    # Kill by PID file
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "Processo $pid finalizado"
        } catch {}
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }

    # Kill processes on port
    $connections = netstat -ano | Select-String ":$Port" | Select-String "LISTENING"
    foreach ($conn in $connections) {
        $parts = $conn -split '\s+'
        $processId = $parts[-1]
        if ($processId -match '^\d+$') {
            try {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Write-Host "Processo $processId na porta $Port finalizado"
            } catch {}
        }
    }

    # Kill Python processes running uvicorn
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*uvicorn*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue

    Write-Host "Servidor parado" -ForegroundColor Green
}

function Clear-PythonCache {
    Write-Host "Limpando cache Python..." -ForegroundColor Yellow

    Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -File -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

    Write-Host "Cache limpo" -ForegroundColor Green
}

function Start-DevServer {
    Write-Host "Iniciando servidor de desenvolvimento..." -ForegroundColor Yellow

    # Check if .env exists
    if (-not (Test-Path ".env")) {
        Write-Host "Erro: arquivo .env nao encontrado" -ForegroundColor Red
        Write-Host "Copie .env.local para .env ou crie um arquivo .env"
        exit 1
    }

    # Clear cache first
    Clear-PythonCache

    # Start uvicorn
    $process = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $Port, "--reload" -PassThru -WindowStyle Hidden
    $process.Id | Out-File $PidFile

    # Wait for startup
    Write-Host -NoNewline "Aguardando servidor iniciar"
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$Port/" -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host ""
                Write-Host "Servidor iniciado com sucesso!" -ForegroundColor Green
                Write-Host "  - Docs: http://localhost:$Port/docs"
                Write-Host "  - API:  http://localhost:$Port/api/v1"
                Write-Host "  - PID:  $($process.Id)"
                return
            }
        } catch {}
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 1
    }

    Write-Host ""
    Write-Host "Erro: servidor nao iniciou em 30 segundos" -ForegroundColor Red
}

function Get-DevServerStatus {
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        try {
            $process = Get-Process -Id $pid -ErrorAction Stop
            Write-Host "Servidor rodando (PID: $pid)" -ForegroundColor Green
            Write-Host "  - URL: http://localhost:$Port"

            # Check if responding
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$Port/" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
                Write-Host "  - Status: Respondendo" -ForegroundColor Green
            } catch {
                Write-Host "  - Status: Nao respondendo" -ForegroundColor Yellow
            }
            return
        } catch {}
    }

    Write-Host "Servidor nao esta rodando" -ForegroundColor Yellow
}

switch ($Action) {
    "start" {
        Stop-DevServer
        Start-DevServer
    }
    "stop" {
        Stop-DevServer
    }
    "restart" {
        Stop-DevServer
        Start-DevServer
    }
    "status" {
        Get-DevServerStatus
    }
}
