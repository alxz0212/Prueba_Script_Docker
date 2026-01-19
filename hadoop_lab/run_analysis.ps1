# Script para ejecutar el Análisis de Hadoop La Liga automáticamente

Write-Host "🐘 Iniciando Entorno de Análisis Hadoop..." -ForegroundColor Cyan

# 1. Verificar e instalar librerías
Write-Host "📦 Verificando librerías necesarias..."
pip install -r requirements.txt | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Podría haber un problema con pip. Intentando continuar..."
}

# 2. Descargar datos si no existen
if (-not (Test-Path "laliga_history.csv")) {
    Write-Host "⬇️  Descargando datos históricos de La Liga..." -ForegroundColor Yellow
    python prepare_data.py
}
else {
    Write-Host "✅ Datos encontrados (laliga_history.csv)." -ForegroundColor Green
}

# 3. Ejecutar MapReduce
Write-Host "⚙️  Ejecutando proceso MapReduce (Esto toma unos segundos)..." -ForegroundColor Cyan
python advanced_stats_mr.py laliga_history.csv > advanced_results.txt 2> $null

# 4. Mostrar Resultados
Write-Host "📊 RESULTADOS DEL ANÁLISIS:" -ForegroundColor Green
python final_stats.py

Write-Host "`n✅ Proceso finalizado."
Pause
