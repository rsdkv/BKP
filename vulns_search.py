import subprocess
import re

def cms_scan(domain):
    
    def remove_ansi_codes(text):
        # Функция для удаления ANSI escape-кодов
        ansi_escape = re.compile(r'\x1b\[.*?m')
        return ansi_escape.sub('', text)

    # Вызов скрипта с передачей аргументов
    out = subprocess.run(["python3", "vulnx.py", "-u", domain, "-e", "--cms"], capture_output=True, text=True)
    
    # Очищаем вывод от ANSI кодов перед его разделением на строки
    clean_output = remove_ansi_codes(out.stdout)

    # Проходим по каждой строке
    lines = clean_output.split('\n')
    results = []
    for line in lines:
        # Условие для проверки наличия знака "[+]"
        if line.strip().startswith('[+]'):
            results.append(line.strip())  # Добавляем строку в список результатов

    for line in results:
        return(line)

# if __name__ == "__main__":
#     cms_scan("https://coin-bank.co/exchange-sberrub-to-ltc/")