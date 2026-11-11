import socket
import threading


# Configuración de red del servidor
# Se utiliza 0.0.0.0 para escuchar en todas las interfaces dentro del contenedor Docker
HOST = '0.0.0.0'
PORT = 5000

# Lista global para almacenar los sockets de los clientes conectados
clientes = []

# Candado (Lock) para evitar condiciones de carrera al modificar la lista de clientes
clientes_lock = threading.Lock()

# Contador para asignar automáticamente a cliente
contador_clientes = 0


def broadcast(mensaje, remitente_socket=None):

    with clientes_lock:
        for cliente in clientes[:]:
            if cliente != remitente_socket:
                try:
                    cliente.sendall(mensaje.encode('utf-8'))
                except Exception:
                    # Si falla el envío, se cierra y elimina el socket inactivo
                    clientes.remove(cliente)
                    cliente.close()


def manejar_cliente(cliente_socket, direccion, nombre_cliente):

    print(f"\r[INFO] {nombre_cliente} conectado desde {direccion}\n[SERVIDOR]: ", end="", flush=True)

    # Informar al cliente cuál es su identificador asignado
    mensaje_bienvenida = f"[INFO] Conectado al servidor como [{nombre_cliente}]"
    cliente_socket.sendall(mensaje_bienvenida.encode('utf-8'))

    # Notificar a los demás participantes que el cliente se ha unido
    broadcast(f"[SERVIDOR]: {nombre_cliente} se ha unido al chat.", cliente_socket)

    while True:
        try:
            # Recibir datos del cliente (hasta 1024 bytes)
            datos = cliente_socket.recv(1024)
            if not datos:
                # Si no hay datos, el cliente cerró la conexión
                break

            texto = datos.decode('utf-8').strip()
            if texto:
                # Formatear el mensaje con el identificador requerido en el examen
                mensaje_formateado = f"[{nombre_cliente}]: {texto}"
                # Mostrar el mensaje en la consola del servidor y restaurar el prompt
                print(f"\r{mensaje_formateado}\n[SERVIDOR]: ", end="", flush=True)
                # Retransmitir el mensaje a los demás clientes conectados
                broadcast(mensaje_formateado, cliente_socket)

        except ConnectionResetError:
            break
        except Exception as e:
            print(f"\r[ERROR] Con {nombre_cliente}: {e}\n[SERVIDOR]: ", end="", flush=True)
            break

    # Limpieza cuando el cliente se desconecta
    with clientes_lock:
        if cliente_socket in clientes:
            clientes.remove(cliente_socket)
    cliente_socket.close()
    print(f"\r[INFO] {nombre_cliente} se ha desconectado.\n[SERVIDOR]: ", end="", flush=True)
    broadcast(f"[SERVIDOR]: {nombre_cliente} ha salido del chat.")


def escribir_servidor():

    while True:
        try:
            texto = input("[SERVIDOR]: ")
            if texto.strip():
                mensaje_formateado = f"[SERVIDOR]: {texto.strip()}"
                # Enviar el mensaje a todos los clientes conectados
                broadcast(mensaje_formateado, remitente_socket=None)
        except EOFError:
            break
        except Exception as e:
            print(f"\r[ERROR SERVIDOR INPUT]: {e}", flush=True)
            break



def iniciar_servidor():

    global contador_clientes

    # Crear socket TCP/IP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permitir reutilizar el puerto inmediatamente si el servidor se reinicia
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST, PORT))
    servidor.listen(5)
    print(f"[INFO] Servidor TCP escuchando en {HOST}:{PORT}...", flush=True)
    print("[INFO] Escribe cualquier mensaje y presiona Enter para hablar como [SERVIDOR].", flush=True)

    # Iniciar hilo para que el servidor pueda enviar mensajes sin esperar turnos
    hilo_escritura = threading.Thread(target=escribir_servidor, daemon=True)
    hilo_escritura.start()

    # Bucle principal para aceptar múltiples clientes simultáneamente
    while True:
        try:
            cliente_socket, direccion = servidor.accept()
            with clientes_lock:
                contador_clientes += 1
                nombre_cliente = f"CLIENTE {contador_clientes}"
                clientes.append(cliente_socket)

            # Crear e iniciar un hilo independiente para atender al nuevo cliente
            hilo_cliente = threading.Thread(
                target=manejar_cliente,
                args=(cliente_socket, direccion, nombre_cliente),
                daemon=True
            )
            hilo_cliente.start()
        except KeyboardInterrupt:
            print("\n[INFO] Apagando el servidor...", flush=True)
            break

    servidor.close()


if __name__ == "__main__":
    iniciar_servidor()