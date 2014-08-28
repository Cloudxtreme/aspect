#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from datetime import datetime
from notice.models import EmailMessage
thismoment = datetime.now()

for item in EmailMessage.objects.filter(date__lte=thismoment, sent=False):
    item.sendit()