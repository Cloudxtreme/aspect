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


def run_command(command):
    
    p = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            close_fds=True)
    return p.communicate()

for device in Device.objects.filter(devtype__in=ubnt_dev):
    ip = device.interfaces.all()[0].ip.ip
    # Создаем каталог
    cmd = 'mkdir -p /tmp/configs/%s/%s' %(ip,datetime.date.today())    
    run_command(cmd)
    # Выполняем копирование
    path = '/tmp/configs/%s/%s/system.cfg' % (ip,datetime.date.today())
    cmd = """sshpass -p 'yfxfkj' scp -o ConnectTimeout=3 -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null hflbcn@%s:/tmp/system.cfg %s""" % (ip,path)
    # print ip, path
    if run_command(cmd):
        if os.path.exists(path):
            myfile = open(path)
            config = Config()
            config.device = device
            config.attach.save('system.cfg',File(myfile))
            config.save()
