#!/usr/bin/env python3

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import argparse
import time
import os
import urllib.request
from urllib.error import HTTPError, URLError


# Constantes
BANNER = """
____            _     ____
|  _ \ ___  _ __| |_  / ___|  ___ __ _ _ __  _ __   ___ _ __
| |_) / _ \| '__| __| \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
|  __/ (_) | |  | |_   ___) | (_| (_| | | | | | | |  __/ |
|_|   \___/|_|   \__| |____/ \___\__,_|_| |_|_| |_|\___|_|

By: Andreu Seguí Segura
"""
SERVER = '127.0.0.1'
TIMEOUT = 30
PORTS_TO_SCAN = [20, 21, 22, 25, 53, 66, 80, 110, 123, 143, 220, 443, 445, 465, 853, 993, 1433, 1434, 1521, 2082 , 2083, 3306 \
                 , 3307, 3389, 5400, 5432, 5433, 5500, 5600, 5700, 5800, 5900, 6881, 6969, 8000, 8080, 8081, 10000]
THREADS = 500
ENCODING = 'utf-8'

# Diccionario vacio para almacenar las ips y los puertos
hosts = {}

def flags():
    # Creamos el parseador
    parser = argparse.ArgumentParser()
    # Añadimos los argumentos
    parser.add_argument("-s", "--server", default=SERVER, type=str, help="Network IP or Target IP. Default: " + SERVER)
    parser.add_argument("-t", "--threads", type=int, default=THREADS, help="Threads working to scann. The more threads, the faster will be. Default: " + str(THREADS))
    parser.add_argument("-p", "--ports", type=int, nargs="+", default=list(PORTS_TO_SCAN), help="Port or Ports you want to scan. Default: " + str(PORTS_TO_SCAN))
    parser.add_argument("-to", "--timeout", type=int, help="Timeout. Default: " + str(TIMEOUT))
    parser.add_argument("-l", "--log", action="store_true", help="Generating a log. By default no log generated")
    # Parseamos los arumentos al script
    args = parser.parse_args()
    # Devlovemos la variable del nombre del archivo
    return args


def get_public_ip():
    try:
        external_ip = urllib.request.urlopen('https://ident.me').read().decode(ENCODING)
    except (HTTPError, URLError) as error:
        pass                                # future use
    except TIMEOUT:
        # if first server fails, try another url
        try:
            external_ip = urllib.request.urlopen('https://ipinfo.io/ip').read().decode(ENCODING)
        except (HTTPError, URLError) as error:
            pass                            # future use
        except TIMEOUT:
            return ''
        else:
            return external_ip
    else:
        return external_ip


def scan_host(ip, port):
    try:
        # Realiza una búsqueda de DNS inversa para obtener el nombre de host
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        hostname = 'N/A'
    try:
        # Crea un objeto socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Establece un tiempo de espera para la conexión
        sock.settimeout(TIMEOUT)
        # Si no existe la ip en el diccionario agrega un lista de puertos vacia
        if ip not in hosts:
            hosts[ip] = []
        result = sock.connect_ex((ip, port))
        # Muestra el puerto si la conexión es exitosa
        if result == 0:
            try:
                serv = socket.getservbyport(port)
            except Exception:
                serv = 'Service not found'
            print('[\033[32m' + '+' '\033[0m' + '] Port: [{}/{}] OPEN in {}'.format(port, serv, hostname))
            # Agrega el puerto a la lista de puertos para esta IP
            hosts[ip].append(port)
        # Cierra el socket
        sock.close()
    except Exception:
        pass


def generate_log():
    date = datetime.datetime.now()
    date_formated = date.strftime("%Y-%m-%d %H:%M:%S")
    with open('Log-{}.log'.format(date_formated), 'w+') as file:
        file.write('Date: {}\n\n'.format(date_formated))
        for key, value in hosts.items():
            file.write('IP: {} | PORTS: {}\n'.format(key, value))


if __name__ == '__main__':
    os.system('clear')
    print(BANNER)
    # Pasmos los argumentos
    args = flags()
    if args.server:
        SERVER = args.server
    if args.threads:
        THREADS = args.threads
    if args.ports:
        PORTS_TO_SCAN = args.ports
    if args.timeout:
        TIMEOUT = args.timeout
    public_ip = get_public_ip()
    # Establecemos un tiempo
    time_start = time.time()
    # Comprovamos que la ip proporcionada es una 0. Eso significa que es una red y no un host
    if args.server[-1] == '0':
        # Creamos una lista de puertos mas usados, para no tener que comprobar todoslos puertos existentes
        print('Network: {}'.format(SERVER))
        print('Public IP: {}'.format(public_ip))
        print('Threads Working: {}'.format(THREADS))
        print('Ports To Scan: {}'.format(PORTS_TO_SCAN))
        print('Timeout: {}\n'.format(TIMEOUT))
        # Recorremos por todas las Ips de la red
        for host in range(1, 255):
            # Creamos una variable para almacenar el prefijo de la red
            network_prefix = args.server[:-1]
            # Añadimos a cada host la ip correspondiendo segun el prefijo de la red
            host = network_prefix + str(host)
            if hosts.values:
                print('\n{}'.format(host))
                print('\033[31m' + 'Service names may be incorrect!' + '\033[0m')
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                futures = [executor.submit(scan_host,host, port) for port in PORTS_TO_SCAN]
                for future in as_completed(futures):
                    pass
        # Acabamos el tiempo para hacer un recuento total de los segundos que ha tardado el escaner
        time_end = time.time()
        total_time = time_end - time_start
        print('\nThe network has been scanned in {} seconds\n'.format(total_time))
        # Si se ha pasado el argumento de log se generara, si no no se generara nada
        if args.log:
            generate_log()
            input('The log has been genereated. Press [enter] to close the program')
            pass
        else:
            input('The log has not been generated. Press [enter] to close the program')
            pass
    else:
        print('Target IP: {}'.format(SERVER))
        print('Public IP: {}'.format(public_ip))
        print('Threads Working: {}'.format(THREADS))
        print('Ports To Scan: {}'.format(PORTS_TO_SCAN))
        print('Timeout: {}'.format(TIMEOUT))
        # Definimos que trabajen todos hilos
        print("\nIP: {}".format(SERVER))
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(scan_host,args.server, port) for port in PORTS_TO_SCAN]
            for future in as_completed(futures):
                pass
        # Acabamos el tiempo para hacer un recuento total de los segundos que ha tardado el escaner
        time_end = time.time()
        total_time = time_end - time_start
        print('\nThe network has been scanned in {} seconds'.format(total_time))
        # Si se ha pasado el argumento de log se generara, si no no se generara nada
        if args.log:
            generate_log()
            input('The log has been genereated. Press [enter] to close the program')
            pass
        else:
            input('The log has not been generated. Press [enter] to close the program')
            pass
