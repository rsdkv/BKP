import telebot
from telebot import types
import shodan
import credential
import traceback
import get_ip_for_host
import shodan_info


TOKEN = credential.telegramtoken()
bot = telebot.TeleBot(TOKEN)
global global_domain_name


@bot.message_handler(commands=['start'])
def start(m):
    try:
        name = m.from_user.first_name
        markup_inline = types.InlineKeyboardMarkup()
        confirmed = types.InlineKeyboardButton(text='Подтвердить', callback_data='confirm')
        markup_inline.add(confirmed)
        msg = bot.send_message(m.chat.id, 'Добро пожаловать, {}!\nЭто инструмент RPS Killer\nНажимаю кнопку согласится вы подтверждаете, что вся ответсвеность за пользование ботом лежит на вас.'.format(name),reply_markup=markup_inline)
        bot.register_next_step_handler(msg,main)
    except:
        bot.send_message(m.chat.id, "Ошибка start")
        print(traceback.format_exc())
        start(m)


@bot.message_handler(content_types=['text'])
def main(m):
    try:
        global global_domain_name
        markup_inline = types.InlineKeyboardMarkup()
        shodan = types.InlineKeyboardButton(text='Сканирование', callback_data='shodan')
        markup_inline.add(shodan)
        global_domain_name = m.text
        real_ip_address = get_ip_for_host.get_ip_by_hostname(m.text)
        if 'Invalid' in real_ip_address:
            bot.send_message(m.chat.id, 'Адрес не найден')
        else:
            bot.send_message(m.chat.id, real_ip_address, reply_markup=markup_inline)
    except:
        bot.send_message(m.chat.id, 'Ошибка в функции main')
        print(traceback.format_exc())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data:
            if call.data == 'confirm':
                bot.send_message(call.message.chat.id, '✅ Вы приняли пользовательские правила')
            elif call.data == 'dos':
                bot.edit_message_text(inline_message_id=call.inline_message_id, text='1')
            elif call.data == 'nmap':
                bot.edit_message_text(inline_message_id=call.inline_message_id, text='1')
            elif call.data == 'shodan':
                r = ''.join(map(str, shodan_info.host_s(call.message.text, global_domain_name)))
                markup_inline = types.InlineKeyboardMarkup()
                vulns = types.InlineKeyboardButton(text='Уязвимости', callback_data='vulns')
                dos = types.InlineKeyboardButton(text='DoS', callback_data='dos')
                markup_inline.add(vulns)
                markup_inline.add(dos)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=r, reply_markup=markup_inline)
    except:
        bot.send_message(call.message.chat.id, 'Ошибка в функции callback_inline')
        print(traceback.format_exc())



if __name__ == '__main__':
    bot.polling(none_stop=True)
shodan_info.py
import shodan
import click
from shodan.helpers import get_ip
import credential
import osWAFscan

#RwhzAhS33ZTwpx8Q9hxAP5ZWxQdsBf1q
SHODAN_API_KEY = credential.shodantoken(RwhzAhS33ZTwpx8Q9hxAP5ZWxQdsBf1q)
api = shodan.Shodan(SHODAN_API_KEY)


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
