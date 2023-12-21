#! /bin/bash

# Creamos volumen para los datos solo si este no existe
IMAGE_NAME="production-kpis:latest"
CONTAINER_NAME="production-kpis-container"

# Verificar si la imagen ya existe
if docker image ls -q "$IMAGE_NAME" | grep -q .; then
    echo "La imagen $IMAGE_NAME ya existe."
else
    # Construir la imagen si no existe
    docker build -t "$IMAGE_NAME" .
    echo "La imagen $IMAGE_NAME ha sido creada."
fi

# Verificar si el contenedor ya existe
if docker ps -a --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    echo "El contenedor $CONTAINER_NAME ya existe."
else
    # Crear el contenedor si no existe
    docker run -d \
    --name $CONTAINER_NAME \
    -p 80:8501 \
    $IMAGE_NAME
    echo "El contenedor $CONTAINER_NAME ha sido creado."
fi

# Iniciar el contenedor si no está en ejecución
if ! docker ps -q --filter "name=$CONTAINER_NAME"; then
    docker start "$CONTAINER_NAME"
    echo "El contenedor $CONTAINER_NAME ha sido iniciado."
fi