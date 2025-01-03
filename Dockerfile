# Usamos una imagen base de Python liviana
FROM python:3.10-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias (opcional)
# Descomenta y ajusta la siguiente línea si necesitas paquetes del sistema
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copiamos el archivo de dependencias
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido del proyecto al directorio de trabajo
COPY . .

# Definimos la variable de entorno para que Python no genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Definimos la variable de entorno para que Python no almacene el buffer de salida
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el bot
CMD ["python", "src/main.py"]
