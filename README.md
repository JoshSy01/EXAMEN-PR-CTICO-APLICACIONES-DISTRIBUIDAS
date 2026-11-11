# EXAMEN PRÁCTICO - APLICACIONES DISTRIBUIDAS

Sistema de chat grupal TCP/IP concurrente donde el servidor se ejecuta dentro de un contenedor Docker y múltiples clientes se conectan desde terminales locales.

## Requisitos previos

- **Docker Desktop** instalado y en ejecución.
- **Python 3** instalado en la máquina local.

---

## Instrucciones de ejecución individual

Abre terminales independientes ubicadas en la carpeta del proyecto:

### 1. Iniciar el Servidor en Docker (Terminal 1)

Ejecuta el siguiente comando para levantar el contenedor del servidor con el puerto `5000` publicado y la terminal interactiva habilitada:

```bash
docker compose run -it --rm --service-ports servidor-chat
```

**¿Qué hace cada parte del comando?**
- **`docker compose run`**: Ejecuta un servicio del `docker-compose.yml` conectando la terminal directamente al proceso (a diferencia de `up`, que no conecta el teclado).
- **`-it`**: Habilita el modo interactivo (`-i`) y una consola virtual (`-t`) para poder escribir mensajes como `[SERVIDOR]:` desde esa terminal.
- **`--rm`**: Elimina automáticamente el contenedor al detenerlo (`Ctrl + C`) para no dejar contenedores detenidos.
- **`--service-ports`**: Publica los puertos definidos en el servicio (`5000:5000`) para que los clientes locales puedan conectarse.
- **`servidor-chat`**: Nombre del servicio a ejecutar definido en `docker-compose.yml`.

### 2. Iniciar el Cliente 1 en local (Terminal 2)

En una nueva terminal local (fuera de Docker), ejecuta:

```bash
python cliente.py
```

El servidor le asignará automáticamente el identificador `[CLIENTE 1]`.

### 3. Iniciar el Cliente 2 en local (Terminal 3)

En otra terminal local adicional, vuelve a ejecutar:

```bash
python cliente.py
```

El servidor le asignará automáticamente el identificador `[CLIENTE 2]`.
---

## Uso del Chat

- **Desde cualquier cliente:** Escribe un mensaje y presiona `Enter` para enviarlo al servidor y a todos los demás clientes conectados (`[CLIENTE X]: mensaje`).
- **Desde el servidor (Docker):** Escribe un mensaje en la terminal donde corre el contenedor y presiona `Enter` para enviarlo a todos los clientes conectados (`[SERVIDOR]: mensaje`).
- **Desconectar un cliente:** Escribe `salir` y presiona `Enter` (o presiona `Ctrl + C`).
- **Detener el servidor:** En la terminal del servidor presiona `Ctrl + C`. Si quedó algún contenedor activo en segundo plano, puedes limpiarlo con:
  ```bash
  docker compose down
  ```
