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
    count = Device.objects.all().count()
    for idx,device in Device.objects.all():
        print (idx/count)
        # device._get_config()

if __name__ == '__main__':
    main_cycle()