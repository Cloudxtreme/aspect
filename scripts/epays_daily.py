#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт добавляет электронные платежи за вчерашний день
import os
import sys
import syslog
import re
import MySQLdb
import requests
from requests.auth import HTTPDigestAuth
from django.db import IntegrityError
from datetime import datetime, time
from datetime import timedelta

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from users.models import Abonent, Plan, TypeOfService, Segment, Service, Passport
from pays.models import Payment, PaymentSystem
from vlans.models import Location

# Получаем платежи OSMP
def importosmp1cdb(cursor,clients,period):
    sql = """SELECT o.txn_id, o.sum, o.date, o.time, s.SubscriberID FROM Subscribers AS s, OSMP_reestr as o WHERE s.SubscriberID=o.SubscriberID AND s.SubscriberID LIKE '%s' AND s.tarif > 1  AND o.date >= '%s'""" % (clients,period)
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
            try:
                payment.save()
            # except IntegrityError as e:
            except:
                msg =  '%s Дублированный платеж' % payment
                syslog.syslog(syslog.LOG_ERR, msg)
            else:
                msg = '%s Платеж зачислен' % payment
                syslog.syslog(syslog.LOG_INFO, msg)

# Получаем платежи Unitellera
def importuntlcdb(cursor,clients,period):
    sql = """SELECT u.Order_IDP, u.summ, u.time_create, s.SubscriberID, u.canceled FROM Subscribers AS s, Uniteller_reestr as u WHERE s.SubscriberID=u.SubscriberID AND s.SubscriberID LIKE '%s' AND u.paid = 1 AND u.canceled = 0 AND u.time_create >= '%s'""" % (clients,period)
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
            try:
                payment.save()
            # except IntegrityError as e:
            except:
                msg =  '%s Дублированный платеж' % payment
                syslog.syslog(syslog.LOG_ERR, msg)
            else:
                msg = '%s Платеж зачислен' % payment
                syslog.syslog(syslog.LOG_INFO, msg)

# Проверка на изменение тарифного плана абонентов
def check_plan(cursor,abonent_id=0):
    abonent_list = Abonent.objects.filter(utype='F') if abonent_id == 0 else Abonent.objects.filter(id=abonent_id)
    for abonent in abonent_list:
        sql = """SELECT SubscriberID, tarif FROM Subscribers WHERE SubscriberID='%s';""" % abonent.contract
        cursor.execute(sql)
        data = cursor.fetchall()
        for rec in data:
            uid,tarifid = rec
            if abonent.service_set.all().count() == 1:
                service = abonent.service_set.all().first()
                if service.plan.id - 1000 != tarifid:
                    try:
                        plan = Plan.objects.get(pk=1000+tarifid)
                    except:
                        msg =  '%s Невозможно найти тарифный план № %' % tarifid
                        syslog.syslog(syslog.LOG_ERR, msg)                        
                    else:
                        service.plan = plan
                        service.save()
                        msg = '%s Тариф изменен' % abonent
                        syslog.syslog(syslog.LOG_INFO, msg)

# Проверка баланса пользователей
def check_balance(abonent_id=0):
    s = requests.Session()
    r = s.get('http://agent.albeon.ru:1180/', auth=HTTPDigestAuth('aspekt', 'sapekt123'))
    abonent_list = Abonent.objects.filter(utype='F') if abonent_id == 0 else Abonent.objects.filter(id=abonent_id)
    
    for abonent in abonent_list:
        balance = 0
        payload = {'SubscriberID':abonent.contract}
        r = s.get('http://agent.albeon.ru:1180/agent/full_fiz.asp', params=payload, auth=HTTPDigestAuth('aspekt', 'sapekt123'))
        html = r.content.decode('cp1251')

        status_str = u'Кредит:'
        if html.find(status_str) == -1:
            balance_str = u'Баланс: ([-]?\d+[.]?\d*) руб.' 
        else:
            balance_str = u'Остаток: ([-]?\d+[.]?\d*) руб.' # У абонента обещанный платеж

        result = re.findall(balance_str, html)
        if len(result):
            balance = float(result[0])

        if abonent.balance != balance:
            msg = '%s баланс: %s  => %s' % (abonent, abonent.balance, balance)
            syslog.syslog(syslog.LOG_INFO, msg)
            abonent.balance = balance
            abonent.save()

def check_clients(clients,cursor):
    sql = """SELECT s.tarif, s.FIO, s.SubscriberID, s.State, s.AddressOfService, s.PasportS, s.PasportN, s.PasportWhon, s.PasportWhen, s.Address FROM Subscribers AS s, Tarifs as t WHERE s.tarif=t.tarifid AND s.SubscriberID LIKE '%s' AND s.tarif > 1 AND s.FIO!='<b>Фамилия Имя отчество</b>';""" % clients
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:
        plan_id, title, contract, state, address, pass_ser, pass_num, pass_who, pass_when, pass_addr = rec
        abonent, created = Abonent.objects.get_or_create(contract=contract, defaults={
                          'title' : title,
                          'contract' :contract,
                          'status': 'A' if state else 'N',
                          'utype' :'F',
                          'is_credit' : 'R',
                        })
        
        if created:
            msg = 'Создан абонент %s' % abonent
            syslog.syslog(syslog.LOG_INFO, msg)          

            try:
                plan = Plan.objects.get(pk=plan_id+1000)
            except:
                pass

            tos = TypeOfService.objects.get(pk=4) # Интернет PPTP id=4
            segment = Segment.objects.get(pk=1) # Основной сегмент
            location = Location(bs_type='C',address=address)
            location.save()
            # Создаем услугу
            service = Service(
                    abon=abonent,
                    tos=tos,
                    segment=segment,
                    location=location,
                    plan=plan,
                    status='A' if state else 'N',
                    )
            service.save()
            # Создаем паспортные данные
            passport = Passport(
                            abonent=abonent,
                            series = pass_ser,
                            number = pass_num,
                            date = pass_when,
                            issued_by = pass_who,
                            address = pass_addr
                            )
            passport.save()

if __name__ == '__main__':
    clients = '50______'
    # clients = '50600007'
    period = (datetime.now() - timedelta(hours=24)).date()
    db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                         passwd="Aa12345", db="radius", charset='utf8')
    cursor = db.cursor()

    check_clients(clients,cursor)               # Проверяем нет ли новых абонентов
    importuntlcdb(cursor,clients,period)        # Проверяем платежи по Uniteller
    importosmp1cdb(cursor,clients,period)       # Проверяем платежи по OSMP
    check_plan(cursor)                          # Проверяем не изменились ли тарифные планы
    check_balance()                             # Синхронизируем балансы
    db.close()