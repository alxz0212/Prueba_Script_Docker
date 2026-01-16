# Script de Setup Simplificado v3

Write-Host "Iniciando script v3..."

function Check-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "⚠️  Este script necesita permisos de Administrador." -ForegroundColor Red
        Write-Host "Por favor, ciérralo y ejecútalo como Administrador." -ForegroundColor Yellow
        Write-Host "(Click derecho -> Ejecutar como administrador)"
        Pause
        exit
    }
}

function Get-Drive {
    Write-Host "Detectando Discos..."
    $Unidades = Get-Volume | Where-Object { $_.DriveLetter -ne $null -and $_.DriveLetter -ne 'C' -and $_.DriveType -eq 'Fixed' }
    
    # Auto-selección inteligente
    $AutoDrive = $Unidades | Where-Object { $_.DriveLetter -eq 'D' }
    if ($AutoDrive) {
        Write-Host "Disco [D] detectado automáticamente. Seleccionándolo..." -ForegroundColor Green
        return 'D'
    }
    if ($Unidades.Count -eq 1) {
        $Letter = $Unidades[0].DriveLetter
        Write-Host "Único disco detectado [$Letter]. Seleccionándolo automáticamente..." -ForegroundColor Green
        return $Letter
    }

    Write-Host "--- Discos Disponibles ---"
    foreach ($u in $Unidades) { 
        Write-Host " [$($u.DriveLetter)] - $($u.FileSystemLabel) ($([math]::round($u.SizeRemaining / 1GB, 2)) GB libres)" 
    }
    Write-Host "--------------------------"

    while ($true) {
        $InputLetter = Read-Host "Escribe la LETRA de tu disco SSD (Ejemplo: E)"
        $CleanLetter = $InputLetter -replace ":", "" -replace " ", ""
        if ($Unidades.DriveLetter -contains $CleanLetter) {
            return $CleanLetter
        }
        else {
            Write-Warning "Letra inválida."
        }
    }
}

function Setup-Folders {
    param($Drive, $Name)
    $Path = "$($Drive):\BIGDATA_LAB_STORAGE\$Name"
    if (-not (Test-Path "$Path\data")) {
        New-Item -ItemType Directory -Path "$Path\data" -Force | Out-Null
        Write-Host "Carpetas creadas en $Path"
    }
    return $Path
}

function Setup-Link {
    param($Local, $Remote)
    # Solo recrear si no existe o apunta mal (simplificado: recrear siempre para asegurar)
    if (Test-Path $Local) { Remove-Item $Local -Recurse -Force }
    cmd /c "mklink /J `"$Local`" `"$Remote`""
}

# --- Main ---
Check-Admin
if ($PSScriptRoot) { Set-Location $PSScriptRoot }
$Project = (Get-Item .).Name
$Drive = Get-Drive
$RemotePath = Setup-Folders -Drive $Drive -Name $Project
Setup-Link -Local ((Get-Location).Path + "\data") -Remote "$RemotePath\data"

# Crear archivo .env
$EnvFile = ".env"
$EnvContent = "SPARK_DATA_PATH=$RemotePath\data"
Set-Content -Path $EnvFile -Value $EnvContent -Force
Write-Host "Archivo '$EnvFile' configurado."

# Levantar Docker automáticamente
Write-Host "Levantando Docker Compose..." -ForegroundColor Cyan
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Error "Hubo un error al levantar Docker. Revisa que Docker Desktop esté corriendo."
    Pause
}
else {
    Write-Host "¡Todo listo! Contenedores iniciados en segundo plano." -ForegroundColor Green
    Start-Sleep -Seconds 3
}
