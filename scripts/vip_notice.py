#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from users.models import Abonent, Service
from notes.models import Note
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db.models import Q

for item in Abonent.objects.filter(vip=True):
    for user in Group.objects.get(name='VIP Мониторинг').user_set.all():
        url = reverse('abonent_info', args=[item.pk])
        new_note = Note(
            title = u'Уведомление о действующем VIP статусе',
            descr = u'У абонента <a href=%s>%s</a> действует VIP статус, проверьте его необходимость' % (url,item.title )  ,
            marks = 'panel-danger',
            author = user,
            )
        new_note.save()

for item in Service.objects.filter(~Q(adm_status = '0'))|Service.objects.filter(speed_in__gt=0)|Service.objects.filter(speed_out__gt=0):
    print item    
    for user in Group.objects.get(name='Инженеры').user_set.all():
        url = reverse('abonent_info', args=[item.abon.pk])
        new_note = Note(
            title = u'Уведомление об измененых параметрах доступа',
            descr = u'У абонента <a href=%s>%s</a> включен административный статус, проверьте его необходимость' % (url,item.abon.title )  ,
            marks = 'panel-info',
            author = user,
            )
        new_note.save()

for item in Service.objects.filter(tos__pk=1,status__in=['A','N'],ip=None):
    for user in Group.objects.get(name='Инженеры').user_set.all():
        url = reverse('abonent_info', args=[item.abon.pk])
        new_note = Note(
            title = u'Отсутствует IP адрес на услуге',
            descr = u'У абонента <a href=%s>%s</a> на услуге [%s] не проставлен IP-адрес' % (url,item.abon.title,item.pk)  ,
            marks = 'panel-warning',
            author = user,
            )
        new_note.save()