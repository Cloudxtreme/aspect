# -*- coding: utf-8 -*- 
from django.db import models
from vlans.models import IPAddr, Vlan

class DevType(models.Model):
    TYPE_OF_SUPPLY = (
        ('5V', '5V'),
        ('12V', '12V'),
        ('24V', '24V'),
        ('220V', '220V'),
    )
    vendor = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, null=True)
    supply = models.CharField(u'Питание', max_length = 4, 
                              choices=TYPE_OF_SUPPLY)
    ports = models.IntegerField(u'Количество портов')

    class Meta:
        verbose_name = u'Тип устройства'
        verbose_name_plural = u'Типы устройств'

    def __unicode__(self):
        return "%s - %s" % (self.vendor, self.model)

def dec2ip(ip):
     return '.'.join([str((ip >> 8 * i) & 255) for i in range(3, -1, -1)])

def ip2dec(ip):
    return sum([int(q) << i * 8 for i, q in enumerate(reversed(ip.split(".")))])

def calcnet(net, mask):
    mask1 = mask + 1
    net1 = dec2ip(ip2dec(net)+pow(2,31-mask))
    if mask >= 29:
        return (net,mask1),(net1,mask1)
    return ((net,mask1),(net1,mask1), calcnet(net,mask1),calcnet(net1,mask1))

class Device(models.Model):
    # TYPE_OF_CHECK = (
    #     ('NC','Не проверять'),
    #     ('PC','ICMP Проверка'),
    #     ('SC','SNMP Проверка'),
    # )
    title = models.CharField(u'Название', max_length=30)
    ip = models.OneToOneField(IPAddr, verbose_name=u'IP адрес', 
        blank=True, null= True)
    mgmt_vlan = models.ForeignKey(Vlan, related_name='mgmt_vlan',
        verbose_name=u'VLAN управления', blank=True, null= True)
    devtype = models.ForeignKey(DevType, verbose_name=u'Модель')
    is_rooter = models.BooleanField(u'Роутер?',default=False)
    mac = models.CharField(u'MAC адрес', blank=True, null= True, max_length=20)
    sn = models.CharField(u'Серийный номер', blank=True, 
                                 null=True, max_length=20)
    # node = models.ForeignKey(Node, verbose_name=u'Местонахождение')
    # check_type = models.CharField(u'Тип проверки', max_length = 2, 
        # choices=TYPE_OF_CHECK)
    # snmp_community = models.CharField(max_length = 20, blank=True, null= True)
    last_available = models.DateTimeField(auto_now=False, auto_now_add=False, 
        blank=True, null=True, verbose_name=u'Последний ответ')

    class Meta:
        verbose_name = u'Устройство'
        verbose_name_plural = u'Устройства'

    def __unicode__(self):
        return "%s - %s - %s - %s" % (self.pk, self.devtype, self.title, self.ip)

class DeviceStatusEntry(models.Model):
    device = models.ForeignKey(Device, verbose_name=u'Устройство')
    state_up = models.BooleanField(u'Up',default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = u'Изменение статуса устройства'
        verbose_name_plural = u'Изменение статусов устройств'
        ordering = ['date']

    def __unicode__(self):
        state = 'up' if self.state_up else 'down'
        return "[%s] %s - is now %s " % (self.date, self.device, state)