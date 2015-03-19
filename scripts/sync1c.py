#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт импорта данных из 1С
import os
import sys
import MySQLdb
import datetime

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from users.models import Abonent, Plan, TypeOfService, Segment, Service, Passport
from vlans.models import Location

db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                         passwd="Aa12345", db="radius", charset='utf8')

cursor = db.cursor()

sql = """SELECT s.tarif, s.FIO, s.SubscriberID, s.State, s.AddressOfService, s.PasportS, s.PasportN, s.PasportWhon, s.PasportWhen, s.Address FROM Subscribers AS s, Tarifs as t WHERE s.tarif=t.tarifid AND s.SubscriberID LIKE '50______' AND s.tarif > 1 AND s.FIO!='<b>Фамилия Имя отчество</b>';"""
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
        print u'Создан абонент #%s - %s' % (abonent.contract,abonent.title)

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

db.close()