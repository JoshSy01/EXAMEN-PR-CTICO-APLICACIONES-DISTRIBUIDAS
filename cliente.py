import socket
import threading

# Dirección de la máquina anfitriona donde Docker publica el puerto del servidor
HOST = '127.0.0.1'
PORT = 5000


def recibir_mensajes(cliente_socket, prompt):

    while True:
        try:
            datos = cliente_socket.recv(1024)
            if not datos:
                print("\r[INFO] El servidor cerró la conexión.", flush=True)
                break
            mensaje = datos.decode('utf-8')
            print(f"\r{mensaje}\n{prompt}", end="", flush=True)
        except Exception:
            print("\r[INFO] Desconectado del servidor.", flush=True)
            break


def enviar_mensajes(cliente_socket, prompt):

    while True:
        try:
            mensaje = input(prompt)
            if mensaje.strip().lower() == 'salir':
                cliente_socket.close()
                break
            if mensaje.strip():
                cliente_socket.sendall(mensaje.encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            cliente_socket.close()
            break
        except Exception as e:
            print(f"[ERROR] No se pudo enviar el mensaje: {e}")
            break


def iniciar_cliente():

    # Crear socket TCP/IP
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar a {HOST}:{PORT}. Verifica que el contenedor Docker esté activo.")
        return

    # Recibir el mensaje inicial de bienvenida para conocer el identificador asignado
    prompt = "[CLIENTE]: "
    try:
        datos_iniciales = cliente.recv(1024).decode('utf-8')
        if datos_iniciales:
            print(datos_iniciales, flush=True)
            if "Conectado al servidor como [" in datos_iniciales:
                nombre_cliente = datos_iniciales.split("Conectado al servidor como [")[1].split("]")[0]
                prompt = f"[{nombre_cliente}]: "
    except Exception:
        print("[ERROR] No se pudo recibir la confirmación inicial del servidor.")
        cliente.close()
        return

    # Crear e iniciar el hilo de escucha en segundo plano (daemon)
    hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(cliente, prompt), daemon=True)
    hilo_recepcion.start()

    # Ejecutar el bucle de envío en el hilo principal mostrando el prompt [CLIENTE X]:
    enviar_mensajes(cliente, prompt)



if __name__ == "__main__":
    iniciar_cliente()