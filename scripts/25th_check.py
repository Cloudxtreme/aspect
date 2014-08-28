#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт запускается 25-го числа и выключает абонентов с отрицательным балансом
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from users.models import Abonent

for item in Abonent.objects.filter(is_credit='O',balance__lt=0):
    item.check_status('Проверка баланса 25-го числа')