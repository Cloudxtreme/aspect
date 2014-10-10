#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт запускается 20-го числа и уведомляет юр. лиц об отрицательном балансе
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from users.models import Abonent
from notice.models import AbonentEvent

if len (sys.argv) == 2:
    try:
        abonentevent = AbonentEvent.objects.get(pk=sys.argv[1]) #Номер события получаем из командной строки
    except Exception, e:
        pass
    else:
        extra_keys = {}
        abonent_list = Abonent.objects.filter(balance__lt=0,utype='U') # Получаем список юр лиц с отрицательным балансом
        abonentevent.generate_messages(abonent_list,extra_keys)