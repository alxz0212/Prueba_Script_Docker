# Script de Setup Simplificado v3

Write-Host "Iniciando script v3..."

function Check-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "ERROR: Ejecuta como Administrador."
        exit
    }
}

function Get-Drive {
    Write-Host "Detectando Discos..."
    $Unidades = Get-Volume | Where-Object { $_.DriveLetter -ne $null -and $_.DriveLetter -ne 'C' -and $_.DriveType -eq 'Fixed' }
    
    if ($Unidades.Count -eq 0) {
        Write-Error "No se detectaron discos SSD/HDD adicionales (aparte de C:)."
        Write-Host "Por favor conecta tu disco externo y vuelve a ejecutar el script."
        Pause
        exit
    }

    Write-Host "--- Discos Disponibles ---"
    foreach ($u in $Unidades) { 
        Write-Host " [$($u.DriveLetter)] - $($u.FileSystemLabel) ($([math]::round($u.SizeRemaining / 1GB, 2)) GB libres)" 
    }
    Write-Host "--------------------------"

    while ($true) {
        $InputLetter = Read-Host "Escribe la LETRA de tu disco SSD (Ejemplo: E)"
        
        # Limpiar entrada (quitar espacios y dos puntos si los pone)
        $CleanLetter = $InputLetter -replace ":", "" -replace " ", ""
        
        # Validar si la letra estÃ¡ en la lista de unidades detectadas
        if ($Unidades.DriveLetter -contains $CleanLetter) {
            return $CleanLetter
        }
        else {
            Write-Warning "La letra '$InputLetter' no corresponde a ninguno de los discos listados arriba. Intenta de nuevo."
        }
    }
}

function Setup-Folders {
    param($Drive, $Name)
    $Path = "$($Drive):\BIGDATA_LAB_STORAGE\$Name"
    New-Item -ItemType Directory -Path "$Path\data" -Force | Out-Null
    Write-Host "Carpetas creadas en $Path"
    return $Path
}

function Setup-Link {
    param($Local, $Remote)
    if (Test-Path $Local) { Remove-Item $Local -Recurse -Force }
    cmd /c "mklink /J `"$Local`" `"$Remote`""
}

# --- Main ---
Check-Admin
$Project = (Get-Item .).Name
$Drive = Get-Drive
$RemotePath = Setup-Folders -Drive $Drive -Name $Project
Setup-Link -Local ((Get-Location).Path + "\data") -Remote "$RemotePath\data"

# Crear archivo .env para Docker
$EnvFile = ".env"
$EnvContent = "SPARK_DATA_PATH=$RemotePath\data"
Set-Content -Path $EnvFile -Value $EnvContent -Force
Write-Host "Archivo '$EnvFile' creado con: $EnvContent"

Write-Host "Listo. Ejecuta 'docker compose up -d' manualmente."
Pause
