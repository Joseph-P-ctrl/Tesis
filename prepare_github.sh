#!/bin/bash

# Script para preparar el proyecto para GitHub y Streamlit Cloud

echo "=== Preparando MicroExpr para Despliegue ==="

# 1. Inicializar Git si no existe
if [ ! -d ".git" ]; then
    echo "Inicializando repositorio Git..."
    git init
    git config user.email "cliente@microexpr.com"
    git config user.name "MicroExpr Client"
else
    echo "Git ya inicializado."
fi

# 2. Agregar todos los archivos
echo "Agregando archivos..."
git add .

# 3. Crear primer commit
echo "Creando commit inicial..."
git commit -m "MicroExpr - App de Detección de Microexpresiones Faciales"

echo ""
echo "✅ Proyecto listo para subir a GitHub"
echo ""
echo "Próximos pasos:"
echo "1. Crear un nuevo repositorio en GitHub (https://github.com/new)"
echo "2. Ejecutar:"
echo "   git remote add origin https://github.com/TU_USUARIO/microexpr.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Ir a https://share.streamlit.io/ y deployar"
echo ""
