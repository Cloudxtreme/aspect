#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from datetime import datetime
from journaling.models import ServiceStatusChanges, AbonentStatusChanges, ServicePlanChanges

thismoment = datetime.now()

#Ищем запланирование смены статусов услуг
for item in ServiceStatusChanges.objects.filter(date__lte=thismoment, done=False).order('date'):
    item.laststatus = item.service.status
    item.done = True
    item.successfully = item.service.set_status(item.newstatus, item.date)
    item.save()

#Ищем запланирование смены тарифов
for item in ServicePlanChanges.objects.filter(date__lte=thismoment, done=False).order('date'):
    item.done = True
    item.successfully = True
    item.service.plan = item.plan
    item.service.save()
    item.save()

#Ищем запланирование смены статусов абонентов
# for item in AbonentStatusChanges.objects.filter(date__lte=thismoment, done=False):
# 	item.laststatus = item.service.status
# 	item.done = True
# 	item.service.set_status(item.newstatus, primary=False)
# 	item.save()