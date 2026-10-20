#!/bin/bash
# SOP - Simulador de Operaciones Psicologicas: inicio con un clic
SOP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SOP_DIR"

URL="http://localhost:8090"
API="http://localhost:8001/api/health"

echo "============================================"
echo "  SOP - Simulador de Operaciones Psicologicas"
echo "  Instrucción OPSIC · audiencias sintéticas"
echo "============================================"

DC="sudo docker"

# 1) Docker daemon
if ! $DC info >/dev/null 2>&1; then
    echo "[1/3] Iniciando daemon de Docker (pedirá contraseña sudo)..."
    sudo sh -c 'nohup dockerd > /tmp/sop-dockerd.log 2>&1 &' 
    for _ in $(seq 1 45); do
        sleep 1
        $DC info >/dev/null 2>&1 && break
    done
    if ! $DC info >/dev/null 2>&1; then
        echo "ERROR: Docker no arrancó. Ver /tmp/sop-dockerd.log"
        read -r -p "Enter para cerrar..."
        exit 1
    fi
else
    echo "[1/3] Docker ya está corriendo."
fi

# 2) Despliegue (compose solo reconstruye lo que cambió)
echo "[2/3] Verificando/desplegando servicios..."
$DC compose up -d --build || {
    echo "ERROR en deploy. Ejecutar: cd $SOP_DIR && sudo docker compose up -d --build"
    read -r -p "Enter para cerrar..."
    exit 1
}

# 3) Esperar salud del backend y abrir navegador
echo "[3/3] Esperando backend..."
for _ in $(seq 1 60); do
    curl -sf "$API" >/dev/null 2>&1 && break
    sleep 2
done

if curl -sf "$API" >/dev/null 2>&1; then
    echo "      Backend OK -> abriendo $URL"
    firefox "$URL" >/dev/null 2>&1 &
    echo ""
    echo "  Usuario: instructor | sop-instructor-2026"
    echo "  Usuario: alumno     | sop-alumno-2026"
else
    echo "      Backend no responde aún. Revisar:"
    echo "        cd $SOP_DIR && sudo docker compose logs backend"
    firefox "$URL" >/dev/null 2>&1 &
fi
echo ""
read -r -p "Listo. Enter para cerrar esta ventana..."
