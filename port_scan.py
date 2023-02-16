import socket
from concurrent.futures import ThreadPoolExecutor
import datetime

# Constantes
BANNER = """
____            _     ____
|  _ \ ___  _ __| |_  / ___|  ___ __ _ _ __  _ __   ___ _ __
| |_) / _ \| '__| __| \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
|  __/ (_) | |  | |_   ___) | (_| (_| | | | | | | |  __/ |
|_|   \___/|_|   \__| |____/ \___\__,_|_| |_|_| |_|\___|_|

By: Andreu Seguí Segura
"""
IP = '127.0.0.1'
MIN_PORTS = 1
MAX_PORTS = 65535
TIME = 0.1
THREADS = 100

# Lista donde se almacenan los puertos abiertos
ports = []

def scan_port(port):
        # Crea un objeto socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Establece un tiempo de espera para la conexión
        sock.settimeout(TIME)
        result = sock.connect_ex((IP, port))
        # Muestra el puerto si la conexión es exitosa
        if result == 0:
            print('\033[32m[+]\033[0m Puerto: {} [Open]'.format(port))
            ports.append(port)
        # Cierra el socket
        sock.close()


def generate_log():
    date = datetime.datetime.now()
    date_formated = date.strftime("%Y-%m-%d %H:%M:%S")
    with open('ports-{}.txt'.format(date_formated), 'w+') as archivo:
        archivo.write('Los puertos {} están abiertos en la dirección IP {}\nDia y Hora: {}'.format(ports, IP, date_formated))

if __name__ == '__main__':
    print(BANNER)
    # Definimos que trabajen 20 procesos
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for port in range(MIN_PORTS, MAX_PORTS):
            # Enviamos a cada proceso la funcion de escaneo
            executor.submit(scan_port, port)
    print('\n')
    print('Hemos escaneado la dirección IP: {}'.format(IP))
    print('Y hemos encontrado los puertos: {}'.format(ports))
    generate_log()