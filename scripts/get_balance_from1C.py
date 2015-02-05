#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт проверяет изменения баланса абонента
import os
import sys
import re

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from users.models import Abonent

import requests
from requests.auth import HTTPDigestAuth

s = requests.Session()
r = s.get('http://agent.albeon.ru:1180/', auth=HTTPDigestAuth('aspekt', 'sapekt123'))

for abonent in Abonent.objects.filter(utype='F'):
# for abonent in Abonent.objects.filter(contract='50400014'):
    balance = 0
    payload = {'SubscriberID':abonent.contract}
    r = s.get('http://agent.albeon.ru:1180/agent/full_fiz.asp', params=payload, auth=HTTPDigestAuth('aspekt', 'sapekt123'))
    html = r.content.decode('cp1251')

    status_str = u'Кредит:'
    if html.find(status_str) == -1:
        balance_str = u'Баланс: ([-]?\d+[.]?\d*) руб.' 
    else:
        balance_str = u'Остаток: ([-]?\d+[.]?\d*) руб.' # У абонента обещанный платеж

    result = re.findall(balance_str, html)
    if len(result):
        balance = float(result[0])  

    # first_pos = html.find(u'Баланс') + 8
    # last_pos = html.find(u'руб.;') - 1
    # balance = float(html[first_pos:last_pos])
    if abonent.balance != balance:
        print u'%s текущий баланс: %s, новый баланс: %s' % (abonent.contract,abonent.balance,balance)
        abonent.balance = balance
        abonent.save()
    