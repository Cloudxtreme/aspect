#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os,sys,re,time
from datetime import datetime
from os import listdir
from os.path import isfile, join

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from vlans.models import TrafRecord,IPAddr

in_dir = '/var/flow/bras/saved/processed/in/'
out_dir = '/var/flow/bras/saved/processed/out/'

def traffic_analize(w_dir,inbound):
    trList =[]
    onlyfiles = [f for f in listdir(w_dir) if isfile(join(w_dir, f))]
    
    for ffile in onlyfiles:
        m = re.match(r"ft-v05.(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+).(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})*", ffile)
        year = int(m.group('year'))
        month = int(m.group('month'))
        day = int(m.group('day'))
        hour = int(m.group('hour'))
        minutes = int(m.group('min'))
        sec = int(m.group('sec'))
        timestamp = datetime(year,month,day,hour,minutes,sec)

        f = open(ffile)
        for line in f:
            ip, octets = line.split(' ')
            try:
                ipaddr = IPAddr.objects.get(ip=ip)
            else:
                trList += [TrafRecord(
                    ip=ipaddr,
                    octets=octets,
                    inbound=inbound,
                    time=timestamp
                    )]
            except:
                print ip
        f.close()

    TrafRecord.objects.bulk_create(trList)

if __name__ == '__main__':
    traffic_analize(in_dir,True)
    traffic_analize(out_dir,False)