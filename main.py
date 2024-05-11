import telebot
from telebot import types
import shodan
from config import settings
import traceback
import get_ip_for_host
import shodan_info
import vulns_search
from cvedetail import CVESearch


bot = telebot.TeleBot(settings.BOT_TOKEN)
global global_domain_name, c, vulns, count_list

c = CVESearch()

@bot.message_handler(commands=['start'])
def start(m):
    try:
        name = m.from_user.first_name
        markup_inline = types.InlineKeyboardMarkup()
        confirmed = types.InlineKeyboardButton(text='Подтвердить', callback_data='confirm')
        markup_inline.add(confirmed)
        msg = bot.send_message(m.chat.id, 'Добро пожаловать, {}!\nЭто инструмент для проверки безопасности сайта\nНажимаю кнопку согласится вы подтверждаете, что вся ответсвеность за пользование ботом лежит на вас.'.format(name),reply_markup=markup_inline)
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
                bot.send_message(call.message.chat.id, '✅ Вы приняли пользовательские правила \n Введите url сайта для сканирования в формате "site.com"')
            elif call.data == 'dos':
                bot.edit_message_text(inline_message_id=call.inline_message_id, text='1')
            elif call.data == 'nmap':
                bot.edit_message_text(inline_message_id=call.inline_message_id, text='1')
            elif call.data == 'shodan':
                info = shodan_info.host_s(call.message.text, global_domain_name)
                r = ''.join(map(str, info))
                markup_inline = types.InlineKeyboardMarkup()
                vulns = types.InlineKeyboardButton(text='Уязвимости', callback_data='vulns')
                dos = types.InlineKeyboardButton(text='DoS', callback_data='dos')
                for i in range(len(info)):
                    if 'Уязвимости' in info[i]:
                        markup_inline.add(vulns)
                markup_inline.add(dos)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=r, reply_markup=markup_inline)
            # elif call.data == 'vulns':
            #     v = ''.join(map(str, vulns_search.cms_scan(global_domain_name)))
            #     markup_inline = types.InlineKeyboardMarkup()
            #     bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=v, reply_markup=markup_inline)
            elif call.data == 'vulns':
                global count_list
                count_list = 0
                markup_inline_first = types.InlineKeyboardMarkup()
                right_first = types.InlineKeyboardButton(text='➡️', callback_data='right')
                markup_inline_first.add(right_first)
                r = ''.join(call.message.text).split('\n')
                global vulns_lists
                vulns_lists = shodan_info.host_vuln_list(r[0])
                bot.send_message(call.message.chat.id, c.id('{}'.format(vulns_lists[count_list])), reply_markup=markup_inline_first)
            elif call.data == 'left':
                count_list = count_list - 1
                markup_inline_left = types.InlineKeyboardMarkup()
                right = types.InlineKeyboardButton(text='➡️', callback_data='right')
                left = types.InlineKeyboardButton(text='⬅️', callback_data='left')
                if count_list != 0 and count_list != (len(vulns_lists)-1):
                    markup_inline_left.add(left, right)
                elif count_list == 0:
                    markup_inline_left.add(right)
                elif count_list == (len(count_list)-1):
                    markup_inline_left.add(left)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=c.id('{}'.format(vulns_lists[count_list])), reply_markup=markup_inline_left)
            elif call.data == 'right':
                count_list = count_list + 1
                markup_inline_right = types.InlineKeyboardMarkup()
                right = types.InlineKeyboardButton(text='➡️', callback_data='right')
                left = types.InlineKeyboardButton(text='⬅️', callback_data='left')
                if count_list != 0 and count_list != (len(vulns_lists)-1):
                    markup_inline_right.add(left, right)
                elif count_list == 0:
                    markup_inline_right.add(right)
                elif count_list == (len(count_list)-1):
                    markup_inline_right.add(left)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=c.id('{}'.format(vulns_lists[count_list])), reply_markup=markup_inline_right)
 
    except:
        bot.send_message(call.message.chat.id, 'Ошибка в функции callback_inline')
        print(traceback.format_exc())



if __name__ == '__main__':
    bot.polling(none_stop=True)