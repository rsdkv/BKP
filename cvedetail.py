#!/usr/bin/env python3
import requests
from typing import Dict, MutableMapping
from urllib.parse import urljoin
from googletrans import Translator

class CVESearch(object):
    def __init__(self, base_url: str='https://cve.circl.lu/', proxies: MutableMapping[str, str]={}, timeout: int=None, verify: bool=True):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.proxies = proxies
        self.session.headers.update({
            'content-type': 'application/json',
            'User-Agent': 'PyCVESearch - python wrapper'})
        self.timeout = timeout
        self.verify = verify
        self.translator = Translator(service_urls=[
            'translate.google.com',
            'translate.google.ru',
        ])

    def _http_get(self, api_call, query=None):
        if query is None:
            url = urljoin(self.base_url, f'api/{api_call}')
        else:
            url = urljoin(self.base_url, f'api/{api_call}/{query}')
        return self.session.get(url, timeout=self.timeout, verify=self.verify)

    def id(self, param) -> str:
        """ id() returns a dict containing a specific CVE ID and translates the information """
        data = self._http_get('cve', query=param)
        js = data.json()
        try:
            about = js['capec'][0]['name']
            solution = js['capec'][0]['solutions']
            translated_about = self.translator.translate(about, src='en', dest='ru').text
            translated_solution = self.translator.translate(solution, src='en', dest='ru').text
        except:
            about = 'Информация не найдена'
            solution = '-'
            translated_about = 'Information not found'
            translated_solution = '-'

        # Форматирование вывода с переводом
        output = f"Описание {param}:\n {translated_about}\n{translated_solution}\n-----------------\nDescription {param}:\n {about}\n{solution}"

        return output

# Пример использования
# c = CVESearch()
# print(c.id("CVE-2020-15801"))