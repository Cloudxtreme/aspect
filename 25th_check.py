#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

# from datetime import datetime
from users.models import Abonent

for item in Abonent.objects.filter(is_credit='R'):
    item.check_status('Проверка баланса 25-го числа')    