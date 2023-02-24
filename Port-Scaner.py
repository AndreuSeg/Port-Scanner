#!/usr/bin/env python3

import socket
import subprocess
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
TIMEOUT = 30

# Diccionario vacio para almacenar las ips y los puertos
hosts = {}

def flags():
    # Creamos el parseador
    parser = argparse.ArgumentParser()
    # Añadimos los argumentos
    parser.add_argument("-s", "--server", required=True, type=str, help="Network IP or Target IP")
    parser.add_argument("-t", "--threads", required=True, type=int, help="Threads working to scann. The more threads, the faster will be")
    parser.add_argument("-minp", "--minport", required=True, type=int, help="First port to scann. Minimum 1")
    parser.add_argument("-maxp", "--maxport", required=True, type=int, help="Last port to scann. Maximum 65535")
    parser.add_argument("-l", "--log", required=False, action="store_true", help="Generating a log")
    # Parseamos los arumentos al script
    args = parser.parse_args()
    # Devlovemos la variable del nombre del archivo
    return args


def scan_host(ip, port):
    try:
        # Crea un objeto socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Establece un tiempo de espera para la conexión
        sock.settimeout(TIMEOUT)
        output = subprocess.check_output(["ping", "-c", "1", ip])
        if "1 received" in output.decode():
            result = sock.connect_ex((ip, port))
            # Muestra el puerto si la conexión es exitosa
            if result == 0:
                try:
                    serv = socket.getservbyport(port)
                except Exception:
                    serv = 'Service not found'
                print('[\033[32m+\033[0m] IP: {} | Port: [{}/{}] OPEN'.format(ip, port, serv))
                # Si no existe la ip en el diccionario agrega un lista de puertos vacia
                if ip not in hosts:
                    hosts[ip] = []
                # Agrega el puerto a la lista de puertos para esta IP
                hosts[ip].append(port)
            # Cierra el socket
            sock.close()
        else:
            pass
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
    # Establecemos un tiempo
    time_start = time.time()

    # Si los argumentos son invalidos, los definimos de manera que sean validos
    if args.maxport >= 65535:
        args.maxport = 65535
    if args.minport <= 1:
        args.minport = 1
    
    # Comprovamos que la ip proporcionada es una 0. Eso significa que es una red y no un host
    if args.server[-1] == '0':
        # Creamos una lista de puertos mas usados, para no tener que comprobar todoslos puertos existentes
        ports_to_scann = [20, 21, 22, 25, 53, 80, 110, 143, 443, 1433, 1434, 3306, 3307, 5432, 5433, 5900, 8000, 8080]
        print('Network: {}'.format(args.server))
        print('Threads Working: {}'.format(args.threads))
        print('Ports To Scan: {}'.format(ports_to_scann))
        print('Timeout: {}\n'.format(TIMEOUT))
        # Recorremos por todas las Ips de la red
        for host in range(1, 254):
            # Creamos una variable para almacenar el prefijo de la red
            network_prefix = args.server[:-1]
            # Añadimos a cada host la ip correspondiendo segun el prefijo de la red
            host = network_prefix + str(host)
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = [executor.submit(scan_host,host, port) for port in ports_to_scann]
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
        print('Target IP: {}'.format(args.server))
        print('Threads Working: {}'.format(args.threads))
        print('Range of Ports To Scan {} - {}'.format(args.minport, args.maxport))
        print('Timeout: {}\n'.format(TIMEOUT))
        # Definimos que trabajen todos hilos
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(scan_host,args.server, port) for port in range(args.minport, args.maxport)]
            for future in as_completed(futures):
                pass
        # Acabamos el tiempo para hacer un recuento total de los segundos que ha tardado el escaner
        time_end = time.time()
        total_time = time_end - time_start
        print('The network has been scanned in {} seconds\n'.format(total_time))
        # Si se ha pasado el argumento de log se generara, si no no se generara nada
        if args.log:
            generate_log()
            input('The log has been genereated. Press [enter] to close the program')
            pass
        else:
            input('The log has not been generated. Press [enter] to close the program')
            pass