# -*- coding: utf-8 -*-
from users.models import Interface
from devices.models import Device, DevType, get_devtype
from vlans.models import IPAddr
from devices.aux import *
import datetime
import logging

# Сканирование подсети
def scan_network(begin,end):
    logging.basicConfig(filename='report.log',format='%(levelname)s:%(message)s',level=logging.WARNING)
    amount = ip2dec(end) - ip2dec(begin)
    counter = 0
    for ip in [dec2ip(ipaddr) for ipaddr in range(ip2dec(begin),ip2dec(end))]:
        counter += 1.0
        print '%0.2f' % (counter/amount)
        msg = '%s - исследуем' % ip
        logging.debug(msg)
        try:
            device = Device.objects.get(interfaces__ip__ip=ip)
        except: 
            device  = None
        
        line = """ ping -c 1 -W 1 %s""" % ip

        if run_command(line)[0].find('100% packet loss') != -1: # Если не пингуется, то выходим
            msg = '> %s - не пингуется' % ip
            logging.info(msg)
            continue

        devtype = get_devtype(ip)                               # Проверяем, что за тип устройства

        if devtype.vendor == 'Unknown':                         # Проверяем можно ли его получить его модель
            msg = '> %s - Либо это Dir-100, либо неверно указано SNMP community' % ip
            logging.warning(msg)
        else:                                                   # Модель получена
            try:
                ipaddr = IPAddr.objects.get(ip=ip)              # Пробуем получить объект IP-адреса
            except: 
                msg = '> %s - IP-адрес не существует, нужно создать подсеть' % ip            # Упс! Объект IP не создан, надо решать вопрос
                logging.warning(msg)
            else:
                iface, created = Interface.objects.get_or_create(ip__ip=ip, defaults={'ip': ipaddr,'for_device':True })
                ip_list = get_ip_list(ip)
                if ip_list:                                       # У устройства несколько адресов
                    _device = Device.objects.filter(interfaces__ip__ip__in=ip_list).first()

                    if device and _device and (device !=_device): # Cуществуют два разных объекта для одного устройства
                        _device.interfaces.add(iface)             # Перекидываем текущий интерфейс на первый объект
                        _device.router = True
                        _device.devtype = devtype
                        _device.save()
                        device.interfaces.remove(iface)
                        device.save()
                        if device.interfaces.count == 0:
                            device.delete()                       # Удаляем лишний экземпляр
                        msg = '> %s - перепривязан к другому устройству' % ip
                    elif device and (not _device or device ==_device): # Объект существует проводим обследование
                        for _iface in [Interface.objects.filter(ip__ip=ipaddr).first() for ipaddr in ip_list]:
                            if _iface: device.interfaces.add(_iface)
                        device.devtype = devtype
                        device.details_map['explored'] = '%s' % datetime.datetime.now().today()    
                        device.save()
                        msg = '> %s - заполняем список интерфейсов' % ip
                    elif not device and _device:                  # Есть объект, добавляем ему интерфейс с текущим адресом
                        for _iface in [Interface.objects.filter(ip__ip=ipaddr).first() for ipaddr in ip_list]:
                            if _iface: _device.interfaces.add(_iface)
                        _device.details_map['explored'] = '%s' % datetime.datetime.now().today()
                        _device.devtype = devtype
                        _device.router = True
                        _device.save()
                        msg = '> %s - уже привязан к существующему устройству' % ip
                    elif not device and not _device:              # Объекта с таким адресом не существует, создаем
                        _device = Device(devtype=devtype,mgmt_vlan=iface.ip.net.vlan)
                        _device.save()
                        for _iface in [Interface.objects.filter(ip__ip=ipaddr).first() for ipaddr in ip_list]:
                            if _iface: _device.interfaces.add(_iface)
                        _device.interfaces.add(iface)
                        _device.router = True
                        _device.save()
                        msg = '> %s - создано новое устройство с множеством адресов' % ip
                else:                                             # У устройства только один адрес
                    if not device:                                # Создаем устройство, т.к. его не было
                        _device = Device(devtype=devtype,mgmt_vlan=iface.ip.net.vlan)
                        _device.save()
                        _device.interfaces.add(iface)
                        _device.details_map['explored'] = '%s' % datetime.datetime.now().today()
                        _device.save()
                        msg = '> %s - создано новое устройство' % ip
                    else:                                         # Просто проверяем актуальность
                        device.devtype = devtype
                        device.details_map['explored'] = '%s' % datetime.datetime.now().today()
                        device.save()
                        msg = '> %s - без изменений' % ip
                logging.info(msg)