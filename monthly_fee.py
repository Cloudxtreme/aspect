#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from pays.models import WriteOff, WriteOffType
from users.models import Service
import datetime
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
wot = WriteOffType.objects.get(title='Абонентская плата')
today = datetime.date.today()
this_month = today.strftime('%B %Y')
last_month = (today - datetime.timedelta(days=1)).strftime('%B %Y')
descr = 'Абонентская плата за '

for item in Service.objects.filter(status='A'):
    if item.abon.is_credit == 'O':
        comment = descr + last_month
    else:
        comment = descr + this_month
    write_off = WriteOff(abonent=item.abon, service=item, wot=wot,summ=item.plan.price, date=datetime.datetime.now(), comment=comment)
    write_off.save()