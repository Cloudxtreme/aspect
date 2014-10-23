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
ubnt_dev = DevType.objects.filter(vendor='Ubiquiti')

for device in Device.objects.filter(devtype__in=ubnt_dev):
    ip = device.interfaces.all()[0].ip.ip
    # Создаем каталог
    cmd = 'mkdir /tmp/configs/%s' %(ip)    
    PIPE = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
        stderr=subprocess.STDOUT, close_fds=True, cwd='/home/')
    # Выполняем копирование
    cmd = """sshpass -p 'yfxfkj' scp hflbcn@%s:/tmp/system.cfg /tmp/configs/%s/%s.cfg""" % (ip,ip,datetime.date.today())
    PIPE = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
        stderr=subprocess.STDOUT, close_fds=True, cwd='/home/')
    # s = p.stdout.read()
    path = '/home/diamond/configs/%s/%s.cfg' % (ip,datetime.date.today())
    try:
        myfile = open(path)
        config = Config()
        config.device = device
        config.attach.save('system.cfg',File(myfile))
        config.save()
    except:
        pass
        # print 'File not found %s' % device