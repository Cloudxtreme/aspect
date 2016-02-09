#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os,sys,re,time
from datetime import datetime
from os import listdir
from os.path import isfile, join

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from vlans.models import TrafRecord,IPAddr

in_dir = '/var/flow/bras/saved/in/'
out_dir = '/var/flow/bras/saved/out/'

def traffic_analize(w_dir,inbound):
    trList =[]
    onlyfiles = [f for f in listdir(w_dir) if isfile(join(w_dir, f))]
    
    for filename in onlyfiles:
        m = re.match(r"ft-v05.(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+).(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})*", filename)
        year = int(m.group('year'))
        month = int(m.group('month'))
        day = int(m.group('day'))
        hour = int(m.group('hour'))
        minutes = int(m.group('min'))
        sec = int(m.group('sec'))
        timestamp = datetime(year,month,day,hour,minutes,sec)

        f = open(os.path.join(w_dir, filename))
        for line in f:
            ip, octets = line.split(' ')
            try:
                ipaddr = IPAddr.objects.get(ip=ip)
            except:
                print ip, '<< inbound' if inbound  else '>> outbound', octets
            else:
                trList += [TrafRecord(
                    ip=ipaddr,
                    octets=octets,
                    inbound=inbound,
                    time=timestamp
                    )]
        f.close()
        os.rename(os.path.join(w_dir, filename), os.path.join(w_dir, 'processed' ,filename))
    TrafRecord.objects.bulk_create(trList)

if __name__ == '__main__':
    traffic_analize(out_dir,False)
    traffic_analize(in_dir,True)