#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт для сбора конфигов с устройств Ubiquiti
import os
import sys
import subprocess
import datetime

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from devices.models import Device, DevType, Config
from django.core.files import File

def main_cycle():
    amount = Device.objects.all().count()
    idx = 0
    for device in Device.objects.all():
        idx += 1
        print "%s from %s" % (idx, amount)
        device._get_config()
        device._do_measuring()

if __name__ == '__main__':
    main_cycle()
