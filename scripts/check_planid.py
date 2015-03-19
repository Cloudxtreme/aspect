#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт проверяет изменения в тарифном плане
import os
import sys
import syslog

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

import MySQLdb
from users.models import Abonent, Plan

def check plain_id(cursor):
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
                msg = '%s Тариф изменен' % abonent.contract
                syslog.syslog(syslog.LOG_INFO, msg)

if __name__ == '__main__':
    db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                         passwd="Aa12345", db="radius")
    db.set_character_set("cp1251")
    cursor = db.cursor()    
    check plain_id(cursor)
    db.close()