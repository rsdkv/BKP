# import subprocess
# import shodan_info
# import socket

# def getIP(domain):
#     out = subprocess.run(["bash", "/tmp/bypass-firewalls-by-DNS-history/bypass-firewalls-by-DNS-history.sh", "-d", domain, "-a", '-o', '/tmp/test'], capture_output=True)
#     out = out.stdout.split(b"\n")
#     if '+' in out[-2].decode("utf-8"):
#         f = open('/tmp/test', 'r')
#         q = f.read()
#         f.close()
#         print(q)
#         return q
#     else:
#         return f'{socket.gethostbyname(domain)}'


# #файл не нужен, так как будет cloudfail
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
        