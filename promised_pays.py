#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'
STATUS_NEW = 'W'
STATUS_ARCHIVE = 'D'

from pays.models import PromisedPays
from users.models import Service
from datetime import datetime

thismoment = datetime.now()

for item in PromisedPays.objects.filter(datefinish__lte=thismoment):
	if item.pay_onaccount:
		item.close()

# for item in Service.objects.filter(datestart__lte=thismoment, status=STATUS_NEW):
# 	item.start()

# for item in Service.objects.filter(datefinish__lte=thismoment).exclude(status=STATUS_ARCHIVE):
# 	item.stop()