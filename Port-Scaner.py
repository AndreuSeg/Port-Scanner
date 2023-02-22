#!/usr/bin/env python3

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
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
TIMEOUT = 10

# Lista donde se almacenan los puertos abiertos
ports = []

def flags():
    # Creamos el parseador
    parser = argparse.ArgumentParser()
    # Añadimos los argumentos
    parser.add_argument("-s", "--server", required=True, type=str, help="Ip del servidor o de la red.\
    Por Defecto: 127.0.0.1")
    parser.add_argument("-t", "--threads", required=True, type=int, help="Cantidad de hilos trabajando simultaneos. Cuanto mas alto sea el numero mas velocidad de escaneo.\
    Por Defecto 100")
    parser.add_argument("-minp", "--minport", required=True, type=int, help="El primer puerto que vas a escanear. El numeor minimo es 1.\
    Por Defecto 1")
    parser.add_argument("-maxp", "--maxport", required=True, type=int, help="El ultimo puerto que vas a escanear. El numero maximo es 65535.\
    Por Defecto 65535")
    parser.add_argument("-l", "--log", required=False, action="store_true", help="Si indicas este argumento se generara un log")
    # Parseamos los arumentos al script
    args = parser.parse_args()
    # Devlovemos la variable del nombre del archivo
    return args


def scan_host(port):
    try:
        # Crea un objeto socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Establece un tiempo de espera para la conexión
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((args.server, port))
        host = socket.gethostbyaddr(args.server)
        # Si te escaneas a ti mismo, que salga la ip 127.0.0.1
        if host[2][0] == '::1':
            host[2][0] = '127.0.0.1'
        # Muestra el puerto si la conexión es exitosa
        if result == 0:
            try:
                serv = socket.getservbyport(port)
            except Exception:
                serv = 'Nombre no encontrado'
            print('[\033[32m+\033[0m] Ip: {} | Hostname: {} | Puerto: {} [Open] [{}]'.format(host[2][0],host[0], port, serv))
            ports.append(port)
        # Cierra el socket
        sock.close()
    except Exception as error:
        print('[\033[31m-\033[0m]Error: {} | Puerto: {}'.format(error, port))


def generate_log():
    date = datetime.datetime.now()
    date_formated = date.strftime("%Y-%m-%d %H:%M:%S")
    with open('ports-{}.txt'.format(date_formated), 'w+') as archivo:
        archivo.write('Los puertos {} están abiertos en la dirección IP {}\nDia y Hora: {}'.format(ports, args.server, date_formated))

if __name__ == '__main__':
    os.system('clear')
    print(BANNER)
    # Pasmos los argumentos
    args = flags()
    # Si los argumentos son invalidos, los definimos de manera que sean validos
    if args.maxport >= 65535:
        args.maxport = 65535
    if args.minport <= 1:
        args.minport = 1
    print('Ip: {}'.format(args.server))
    print('Hilos tabajando simultaneamente: {}'.format(args.threads))
    print('Rango de puertos a escanear: {} - {}'.format(args.minport, args.maxport))
    print('Timeout de: {} segundos\n'.format(TIMEOUT))
    # Establecemos un tiempo
    time_start = time.time()
    # Definimos que trabajen todos hilos
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(scan_host, port) for port in range(args.minport, args.maxport)]
        for future in as_completed(futures):
            pass
    # Si no se encunetra ningun puerto, envia un mensaje de que no se ha encontrado nada
    if len(ports) == 0:
        print('No se han encontrado puertos')
    # Si se ha encontrado hacer un informe
    else:
        # Acabamos el tiempo para hacer un recuento total de los segundos que ha tardado el escaner
        time_end = time.time()
        total_time = time_end - time_start
        print('\nNumeros de puertos totales: {}'.format(len(ports)))
        print('Estos puertos son: {}'.format(ports))
        print('El objetivo ha sido escaneado en un total de {} segundos\n'.format(total_time))
        # Si se ha pasado el argumento de log se generara, si no no se generara nada
        if args.log:
            generate_log()
            input('Se ha generado un log. Pulsar intro para cerrar el programa')
            pass
        else:
            input('No se ha generado un log. Pulsar intro para cerrar el programa')
            pass