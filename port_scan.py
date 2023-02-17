#!/usr/bin/env python3

import socket
from concurrent.futures import ThreadPoolExecutor
import datetime
import argparse
import time
import os

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
PROCESS = 100

# Lista donde se almacenan los puertos abiertos
ports = []

def flags():
    # Creamos el parseador
    parser = argparse.ArgumentParser()
    # Añadimos los argumentos
    parser.add_argument("-s", "--server", type=str, help="Ip del servidor o de la red.\
    Por Defecto: 127.0.0.1")
    parser.add_argument("-p", "--process", type=int, help="Cantidad de procesos simultaneos. Cuanto mas alto sea el numero mas velocidad de escaneo.\
    Por Defecto 100")
    parser.add_argument("-minp", "--minport", type=int, help="El primer puerto que vas a escanear. El numeor minimo es 1.\
    Por Defecto 1")
    parser.add_argument("-maxp", "--maxport", type=int, help="El ultimo puerto que vas a escanear. El numero maximo es 65535.\
    Por Defecto 65535")
    parser.add_argument("-l", "--log", action="store_true", help="Si indicas este argumento se generara un log")
    # Parseamos los arumentos al script
    args = parser.parse_args()
    # Declaramos los argumentos
    IP = args.server
    PROCESS = args.process
    MIN_PORTS = args.minport
    MAX_PORTS = args.maxport
    log = args.log
    # Devlovemos la variable del nombre del archivo
    return IP, PROCESS, MIN_PORTS , MAX_PORTS, log

def scan_host(port):
        # Crea un objeto socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Establece un tiempo de espera para la conexión
        sock.settimeout(TIME)
        result = sock.connect_ex((IP, port))
        hostname = socket.gethostname()
        # Muestra el puerto si la conexión es exitosa
        if result == 0:
            print('\033[32m[+]\033[0m Hostname: {} | Ip: {} | Puerto: {} [Open]'.format(hostname, IP, port))
            ports.append(port)
        # Cierra el socket
        sock.close()


def generate_log():
    date = datetime.datetime.now()
    date_formated = date.strftime("%Y-%m-%d %H:%M:%S")
    with open('ports-{}.txt'.format(date_formated), 'w+') as archivo:
        archivo.write('Los puertos {} están abiertos en la dirección IP {}\nDia y Hora: {}'.format(ports, IP, date_formated))

if __name__ == '__main__':
    os.system('clear')
    print(BANNER)
    # Pasmos los argumentos
    IP = flags()[0]
    PROCESS = flags()[1]
    MIN_PORTS = flags()[2]
    MAX_PORTS = flags()[3]
    log = flags()[4]
    print('Ip: {}'.format(IP))
    print('Procesos simultaneos: {}'.format(PROCESS))
    print('Rango de puertos a escanear: {} - {}\n'.format(MIN_PORTS, MAX_PORTS))
    time_start = time.time()
    # Definimos que trabajen todos procesos
    with ThreadPoolExecutor(max_workers=PROCESS) as executor:
        for port in range(MIN_PORTS, MAX_PORTS):
                executor.submit(scan_host, port)
    # Si no se encunetra ningun puerto, envia un mensaje de que no se ha encontrado nada
    if len(ports) == 0:
        print('No se han encontrado puertos')
    # Si se ha encontrado hacer un informe
    else:
        time_end = time.time()
        total_time = time_end - time_start
        print('\nNumeros de puertos totales: {}'.format(len(ports)))
        print('Estos puertos son: {}'.format(ports))
        print('El objetivo ha sido escaneado en un total de {} segundos\n'.format(total_time))
        # Si se ha pasado el argumento de log se generara, si no no se generara nada
        if log:
            generate_log()
            input('Se ha generado un log.\nPulsar intro para cerrar el programa:')
            pass
        else:
            input('No se ha generado un log.\nPulsar intro para cerrar el programa:')
            pass