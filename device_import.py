#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'

from devices.models import Device,DevType
from users.models import Interface
from vlans.models import IPAddr

f = open('devices.csv')

for l in f:
    ipaddr,model,comment = l.split(';')
    # print '%s - %s - %s' % (ip,model,description)
    if model =='':
        print 'Пустая запись %s' % ipaddr
    else:
        try:
            ip = IPAddr.objects.get(ip=ipaddr)
        except:
            print '%s - не существует' % ipaddr
        else:
            iface,iface_created = Interface.objects.get_or_create(ip=ip,defaults={'ip' : ip,'for_device' :True})
            devtype,type_created = DevType.objects.get_or_create(model=model,defaults={'vendor': 'Ubiquiti', 'model' : model, 'ports' :1, 'supply' : '220V' })
            if iface_created:
                device = Device(comment=comment,devtype=devtype,mgmt_vlan=iface.ip.net.vlan)
                device.save()
                device.interfaces.add(iface)
            else:
                print 'Странная ситуация iface уже создан %s' % ipaddr

    
    # device, created = Device.objects.get_or_create(number=number, 
    #                 defaults={'number': number,
    #                             'title' : title[0:29], 
    #                      'description' : description,
    #                         })
    # if created:
    #     print u'Создан'
    # else:
    #     print u'Уже есть'