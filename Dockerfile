# Dockerfile para el Servidor de Chat Colaborativo
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY common/ ./common/
COPY server/ ./server/
COPY run_server.py .

# Puerto por defecto (puede ser sobrescrito por la nube)
ENV PORT=8765

# Exponer puerto
EXPOSE ${PORT}

# Comando de inicio
CMD python run_server.py --host 0.0.0.0 --port ${PORT}