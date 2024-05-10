import re
import subprocess
import socket
    
def getIP(domain):
    out = subprocess.run(["python3", "cloudfail.py", "-t", domain], capture_output=True, text=True)
    out = out.stdout.splitlines()
    
    # Скрипт для поиска IP и поддоменов
    ip_addresses = []
    subdomains = []

    for line in out:
        # line = line.decode()  # Декодируем байты в строку

        # Поиск IP после "IP HTTP" или "IP HTTPS"
        ip_search = re.search(r"IP HTTP[S]?: (\d+\.\d+\.\d+\.\d+)", line)
        if ip_search:
            ip_addresses.append(ip_search.group(1))
        
        # Поиск поддомена
        subdomain_search = re.search(r"\[FOUND:SUBDOMAIN\].*HTTP", line)
        if subdomain_search:
            subdomains.append(line)

    if not ip_addresses and not subdomains:
        # print(f'{socket.gethostbyname(domain)}')
        return f'{socket.gethostbyname(domain)}'
    else:
        return(ip_addresses)
        