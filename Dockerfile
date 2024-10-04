# Usar la imagen base de Python 3.9
FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y curl apt-transport-https unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | tee /etc/apt/sources.list.d/msprod.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Crear directorio de la aplicación
WORKDIR /app

# Copiar los archivos de la aplicación
COPY . .

# Instalar las dependencias de Python
RUN pip install -r requirementsAPI.txt

# Exponer el puerto que usará la aplicación (ajustar según sea necesario)
EXPOSE 8000

# Comando para correr la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
