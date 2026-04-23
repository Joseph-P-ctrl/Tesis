Write-Host "=== Preparando MicroExpr para Despliegue ===" -ForegroundColor Cyan

# 1. Verificar si Git está disponible
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git no está instalado. Instálalo desde https://git-scm.com/" -ForegroundColor Red
    exit
}

# 2. Inicializar Git si no existe
if (-not (Test-Path ".\.git")) {
    Write-Host "Inicializando repositorio Git..." -ForegroundColor Green
    git init
    git config user.email "cliente@microexpr.com"
    git config user.name "MicroExpr Client"
} else {
    Write-Host "Git ya inicializado." -ForegroundColor Yellow
}

# 3. Agregar todos los archivos
Write-Host "Agregando archivos..." -ForegroundColor Green
git add .

# 4. Crear primer commit
Write-Host "Creando commit inicial..." -ForegroundColor Green
git commit -m "MicroExpr - App de Detección de Microexpresiones Faciales"

Write-Host ""
Write-Host "✅ Proyecto listo para subir a GitHub" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Crear un nuevo repositorio en GitHub (https://github.com/new)"
Write-Host "2. Ejecutar estos comandos:"
Write-Host "   git remote add origin https://github.com/TU_USUARIO/microexpr.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "3. Ir a https://share.streamlit.io/ y deployar"
Write-Host ""
