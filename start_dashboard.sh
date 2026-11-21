#!/usr/bin/env bash
# Script de arranque automatizado para la Interfaz Centralizada SmartCity Analytics (Sprint 2).
# CE-3101 Bases de Datos | TEC Cartago | Equipo RIC

echo "=========================================================="
echo "  SmartCity Analytics - Panel Centralizado (Sprint 2)"
echo "  CE-3101 Bases de Datos | TEC Cartago | Equipo RIC"
echo "=========================================================="
echo ""

if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "[1/2] Docker activo. Verificando contenedor 'app'..."
    docker compose up -d app
    echo "[2/2] Iniciando Streamlit dentro del contenedor Docker..."
    echo "URL de acceso: http://localhost:8501"
    docker compose exec app streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=8501
else
    echo "[INFO] Docker Daemon no activo o no disponible. Iniciando en modo local (Python)..."
    echo "URL de acceso: http://localhost:8501"
    python3 -m streamlit run dashboard/app.py --server.port=8501 || python -m streamlit run dashboard/app.py --server.port=8501
fi
