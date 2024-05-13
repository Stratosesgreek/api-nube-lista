# Usar la imagen oficial de Python como base
FROM python:3.12.0-slim

# Instalar dependencias necesarias para psql
RUN apt-get update && apt-get install -y postgresql-client

# Establecer el directorio de trabajo en el contenedor
WORKDIR /code

# Copiar el script de espera
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Copiar solo la carpeta con el código fuente
COPY . /code

# Instalar las dependencias
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Comando para ejecutar la aplicación usando Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
