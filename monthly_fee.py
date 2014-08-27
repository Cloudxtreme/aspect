#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from pays.models import WriteOff, WriteOffType
from users.models import Service
import datetime
import calendar
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
wot = WriteOffType.objects.get(title='Абонентская плата')
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
this_month = today.strftime('%B %Y')
last_month = yesterday.strftime('%B %Y')
descr = 'Абонентская плата за '

for item in Service.objects.filter(status='A'):
    # Проверяем тип оплаты, если предоплата, то списываем за следующий месяц, если постоплата, то за предыдущий
    if item.abon.is_credit == 'O':
        comment = descr + last_month
    else:
        comment = descr + this_month
    summ = item.plan.price

    # Доп. проверка на старт услуги в предыдущем месяце
    if (item.datestart.month == yesterday.month) and (item.datestart.year == yesterday.year):
        qty_days = calendar.mdays[item.datestart.month]
        # if item.datefinish and (item.datefinish.month == yesterday.month) and (item.datefinish.year == yesterday.year):
            # summ = item.plan.price * (item.datefinish.day - item.datestart.day + 1)/qty_days 
        # else:
        summ = item.plan.price * (qty_days - item.datestart.day + 1)/qty_days
        comment = 'Абонентская плата за %s за %s дней месяца' % (item.datestart.strftime('%B %Y'), qty_days - item.datestart.day + 1)
        print summ,comment

    write_off = WriteOff(abonent=item.abon, service=item, wot=wot,summ=summ, date=datetime.datetime.now(), comment=comment)
    write_off.save()