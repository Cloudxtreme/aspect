#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт добавляет электронные платежи за вчерашний день
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

import MySQLdb
from datetime import datetime, time
from datetime import timedelta
from users.models import Abonent
from pays.models import Payment, PaymentSystem

db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                         passwd="Aa12345", db="radius", charset='utf8')
cursor = db.cursor()

def importosmp1cdb():
    sql = """SELECT o.txn_id, o.sum, o.date, o.time, s.SubscriberID FROM Subscribers AS s, OSMP_reestr as o WHERE s.SubscriberID=o.SubscriberID AND s.SubscriberID LIKE '50______' AND s.tarif > 1  AND o.date >= '%s'""" % (datetime.now() - timedelta(hours=24)).date()
    cursor.execute(sql)
    data = cursor.fetchall()
    p_ps = PaymentSystem.objects.get(pk=1) # OSMP id=1
    
    payList = []
    for rec in data:
        p_id, p_sum, p_date, p_time, a_contract = rec
        full_time = datetime.combine(p_date,time(0,0)) + p_time
        try:
            p_ab = Abonent.objects.get(contract=a_contract)
        except:
            pass
        else:
            payment = Payment(abonent=p_ab,
                        top = p_ps,
                        summ = p_sum,
                        date = full_time,
                        num = p_id,
                        valid = True,
                        )
            payment.save()
            # payList += [Payment(abon=p_ab,
            #             top = p_ps,
            #             summ = p_sum,
            #             date = full_time,
            #             num = p_id,
            #             valid = True,
            #             )]
    # print payList
    # Payment.objects.bulk_create(payList)

def importuntlcdb():
    sql = """SELECT u.Order_IDP, u.summ, u.time_create, s.SubscriberID, u.canceled FROM Subscribers AS s, Uniteller_reestr as u WHERE s.SubscriberID=u.SubscriberID AND s.SubscriberID LIKE '50______' AND u.paid = 1 AND u.canceled = 0 AND u.time_create >= '%s'""" % (datetime.now() - timedelta(hours=24)).date()
    cursor.execute(sql)
    data = cursor.fetchall()
    p_ps = PaymentSystem.objects.get(pk=2) # Uniteller id=2
    payList = []
    for rec in data:
        p_id, p_sum, p_date, a_contract, p_canceled = rec
        try:
            p_ab = Abonent.objects.get(contract=a_contract)
        except:
            pass
        else:
            payment = Payment(abonent=p_ab,
                            top=p_ps,
                            summ=p_sum,
                            date=p_date,
                            num=p_id,
                            valid=not p_canceled,
                            )
            payment.save()
            # payList += [Payment(abon=p_ab,
            #                 top=p_ps,
            #                 summ=p_sum,
            #                 date=p_date,
            #                 num=p_id,
            #                 valid=not p_canceled,
            #                 )]
    # print payList
    # Payment.objects.bulk_create(payList)

importuntlcdb()
importosmp1cdb()
db.close()