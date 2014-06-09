#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from pays.models import WriteOff, WriteOffType
from users.models import Service
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
wot = WriteOffType.objects.get(title='Абонентская плата')
comment = 'Абонентская плата за ' + datetime.today().strftime('%B %Y')

for item in Service.objects.filter(status='A'):
    write_off = WriteOff(abonent=item.abon, service=item, wot=wot,summ=item.plan.price, date=datetime.now(), comment=comment)
    write_off.save()