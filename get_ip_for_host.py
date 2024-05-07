import socket

def get_ip_by_hostname(hostname):
    try:
        return f'{socket.gethostbyname(hostname)}'
    except socket.gaierror as error:
        return f'Invalid Hostname - {error}'