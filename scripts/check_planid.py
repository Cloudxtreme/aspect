#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*-

# Скрипт проверки тарифного плана пользователей
import sys, os, re

sys.path.append("/home/diamond/venv/dev/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

import MySQLdb
from users.models import Abonent, Plan

db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                     passwd="Aa12345", db="radius")
db.set_character_set("cp1251")
cursor = db.cursor()

for abonent in Abonent.objects.filter(utype='F'):
    sql = """SELECT SubscriberID, tarif FROM Subscribers WHERE SubscriberID='%s';""" % abonent.contract
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:
        uid,tarifid = rec
        service = abonent.service_set.all()[0]
        if service.plan.id - 1000 != tarifid:
            plan = Plan.objects.get(pk=1000+tarifid)
            service.plan = plan
            service.save()
            print u'%s Тариф изменен' % abonent.contract
