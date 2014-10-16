# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from vlans.models import Vlan    

f = open('vlan.csv')

for l in f:
    print l
    number,title,description = l.split(';')
    device, created = Vlan.objects.get_or_create(number=number, 
                    defaults={'number': number,
                                'title' : title[0:29], 
                         'description' : description,
                            })
    if created:
        print u'Создан'
    else:
        print u'Уже есть'