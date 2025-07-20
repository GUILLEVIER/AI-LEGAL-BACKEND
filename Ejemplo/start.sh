#!/bin/bash

# Script para iniciar el generador de documentos
echo "🚀 Iniciando Generador de Documentos..."

# Función para limpiar procesos al salir
cleanup() {
    echo "🛑 Deteniendo servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Iniciar backend
echo "📡 Iniciando servidor backend (Django)..."
cd backend
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!
cd ..

# Esperar un momento para que el backend se inicie
sleep 3

# Iniciar frontend
echo "🎨 Iniciando servidor frontend (React)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Servidores iniciados:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   Admin Django: http://localhost:8000/admin"
echo ""
echo "Presiona Ctrl+C para detener ambos servidores"

# Esperar a que ambos procesos terminen
wait 