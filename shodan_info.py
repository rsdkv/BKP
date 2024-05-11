import shodan
import click
from shodan.helpers import get_ip
import credential
import osWAFscan
from config import settings

api = shodan.Shodan(settings.SHODAN_API_KEY)


def host_print_pretty(host):
    info_lists = [get_ip(host) + '\n']
    if len(host['hostnames']) > 0:
        info_lists.append('🌐 Hostname: ' + ';'.join(host['hostnames']) + '\n')

    if 'city' in host and host['city']:
        info_lists.append('🌆 Город: ' + host['city'] + '\n')

    if 'country_name' in host and host['country_name']:
        info_lists.append('🌍 Страна: ' + host['country_name'] + '\n')

    if 'os' in host and host['os']:
        info_lists.append('💻 Операционная система: ' + host['os'] + '\n')

    if 'org' in host and host['org']:
        info_lists.append('🧰 Организация: ' + host['org'] + '\n')

    if 'last_update' in host and host['last_update']:
        info_lists.append('🔄 Последние сканирование: ' + host['last_update'] + '\n')

    info_lists.append('Количество портов: ' + str(len(host['ports'])) + '\n')

    if 'vulns' in host and len(host['vulns']) > 0:
        vulns = []
        for vuln in host['vulns']:
            if vuln.startswith('!'):
                continue
            if vuln.upper() == 'CVE-2014-0160':
                vulns.append('Heartbleed')
            else:
                vulns.append(vuln)

        if len(vulns) > 0:
            r = (', '.join(map(str, vulns)))
            k = '💀 Уязвимости: ' + r + '\n'
            info_lists.append(k)

    if len(host['ports']) != len(host['data']):
        ports = host['ports']
        for banner in host['data']:
            if banner['port'] in ports:
                ports.remove(banner['port'])

        for port in ports:
            banner = {
                'port': port,
                'transport': 'tcp',
                'timestamp': host['data'][-1]['timestamp'],
                'placeholder': True,
            }
            host['data'].append(banner)

    info_lists.append('Порты:\n')
    a = []
    for banner in sorted(host['data'], key=lambda k: k['port']):
        product = ''
        version = ''
        t = ''
        if 'product' in banner and banner['product']:
            product = banner['product']
        if 'version' in banner and banner['version']:
            version = '({})'.format(banner['version'])

        t = banner['port']
        if 'transport' in banner:
            t = '🔺' + str(t) + '/'
            t = t + banner['transport']
        t = t + ' ' + product + ' ' + version + '\n'
        a.append(t)
        q = (''.join(map(str, a)))
    info_lists.append(q)
    print(info_lists)
    for i in range(len(info_lists)):
        if 'Уязвимости' in info_lists[i]:
            print(1)
    return info_lists


def host_print_tsv(host, history=False):
    for banner in sorted(host['data'], key=lambda k: k['port']):
        click.echo(click.style('{:>7d}'.format(banner['port']), fg='cyan'), nl=False)
        click.echo('\t', nl=False)
        click.echo(click.style('{} '.format(banner['transport']), fg='yellow'), nl=False)

        if history:
            date = banner['timestamp'][:10]
            click.echo(click.style('\t({})'.format(date), fg='white', dim=True), nl=False)
        click.echo('')

def vulns_lists(host):
    if 'vulns' in host and len(host['vulns']) > 0:
        vulns = []
        for vuln in host['vulns']:
            if vuln.startswith('!'):
                continue
            else:
                vulns.append(vuln)

        if len(vulns) > 0:
            return vulns



def host_s(host, global_domain_name):
    r = api.host(host)
    if 'org' in r and r['org']:
        if r['org'] == 'Cloudflare, Inc.' and global_domain_name != str(get_ip(r)):
            two = api.host(osWAFscan.getIP(global_domain_name))
            return host_print_pretty(two)
        else:
            return host_print_pretty(r)
    else:
        return host_print_pretty(r)

def host_vuln_list(host):
    r = api.host(host)
    return vulns_lists(r)