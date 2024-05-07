#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from typing import Optional, Dict, MutableMapping

from urllib.parse import urljoin

# !!! pip install googletrans==4.0.0rc1 !!!
from googletrans import Translator

# Usage:
# from cvedetail import CVESearch
# c = CVESearch()
# print(c.id("CVE-2020-15801"))

class CVESearch(object):

    def __init__(self, base_url: str='https://cve.circl.lu/', proxies: MutableMapping[str, str]={}, timeout: Optional[int]=None, verify=True):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.proxies = proxies
        self.session.headers.update({
            'content-type': 'application/json',
            'User-Agent': 'PyCVESearch - python wrapper'})
        self.timeout = timeout
        self.verify = verify

    def _http_get(self, api_call, query=None):
        if query is None:
            url = urljoin(self.base_url, f'api/{api_call}')
        else:
            url = urljoin(self.base_url, f'api/{api_call}/{query}')
        return self.session.get(url, timeout=self.timeout, verify=self.verify)

    def id(self, param) -> Dict:
        """ id() returns a dict containing a specific CVE ID """
        data = self._http_get('cve', query=param)
        js = data.json()

        about = js['capec'][0]['name']
        solution = js['capec'][0]['solutions']
        
        translator = Translator()

        return f"""Описание {param}: {translator.translate(about, dest="ru").text}\nРешение: {translator.translate(solution, dest="ru").text}"""
