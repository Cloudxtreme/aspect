#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from users.models import Abonent
from notes.models import Note
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

for item in Abonent.objects.filter(vip=True):
    url = reverse('abonent_info', args=[item.pk])
    new_note = Note(
        title = u'Уведомление о действующем VIP статусе',
        descr = u'У абонента <a href=%s>%s</a> действует VIP статус, проверьте его необходимость' % (url,item.title )  ,
        marks = 'panel-danger',
        author = User.objects.get(pk=6),
        )
    new_note.save()