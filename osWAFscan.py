import subprocess
import shodan_info
import socket

def getIP(domain):
    out = subprocess.run(["bash", "/tmp/bypass-firewalls-by-DNS-history/bypass-firewalls-by-DNS-history.sh", "-d", domain, "-a", '-o', '/tmp/test'], capture_output=True)
    out = out.stdout.split(b"\n")
    if '+' in out[-2].decode("utf-8"):
        f = open('/tmp/test', 'r')
        q = f.read()
        f.close()
        print(q)
        return q
    else:
        return f'{socket.gethostbyname(domain)}'