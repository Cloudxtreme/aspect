# -*- coding: utf-8 -*- 
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

# Create your models here.

TYPE_OF_SUPPLY = (
    ('5V', '5V'),
    ('12V', '12V'),
    ('24V', '24V'),
    ('220V', '220V'),
 )

TYPE_OF_OBJECTS = (
    ('C', 'Клиент'),
    ('B', 'Базовая Станция'),
    ('PB','Возможная БС'),
    ('CP','Точка перескока'),
)

NETWORK_USERS = 'UN'
NETWORK_EQUIP = 'EN'
NETWORK_DISTRIB = 'DN'
NETWORK_LIMITER = 'LN'

TYPE_OF_NETS = (
    (NETWORK_USERS,'Сеть пользователей'),
    (NETWORK_EQUIP,'Сеть оборудование'),
    (NETWORK_DISTRIB,'Сеть для распределения'),
    (NETWORK_LIMITER,'Сеть разделитель'),
)

class Vlan(models.Model):
    title = models.CharField(max_length=30)
    number = models.IntegerField()
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = _('Vlan')
        verbose_name_plural = _('Vlans')

    def __unicode__(self):
        return "%s - %s" % (self.number, self.title)

class Node(models.Model):
    title  = models.CharField(max_length=100)
    latlng = models.CharField(u'lat/lon', blank=True, max_length=300)
    bs_type = models.CharField(u'Тип БС', max_length = 2, 
                               choices=TYPE_OF_OBJECTS)

    class Meta:
        verbose_name = u'Адрес'
        verbose_name_plural = u'Адреса'

    def __unicode__(self):
        return "%s - %s - %s" % (self.pk, self.title, self.bs_type)


# class DevType(models.Model):
#     vendor = models.CharField(max_length=50)
#     model = models.CharField(max_length=50)
#     description = models.CharField(max_length=200, blank=True, null=True)
#     supply = models.CharField(u'Питание', max_length = 4, 
#                               choices=TYPE_OF_SUPPLY)
#     ports = models.IntegerField(u'Количество портов')

#     class Meta:
#         verbose_name = _('DevType')
#         verbose_name_plural = _('DevTypes')

#     def __unicode__(self):
#         return "%s - %s" % (self.vendor, self.model)

# def dec2ip(ip):
#      return '.'.join([str((ip >> 8 * i) & 255) for i in range(3, -1, -1)])

# def ip2dec(ip):
#     return sum([int(q) << i * 8 for i, q in enumerate(reversed(ip.split(".")))])

# def calcnet(net, mask):
#     mask1 = mask + 1
#     net1 = dec2ip(ip2dec(net)+pow(2,31-mask))
#     if mask >= 29:
#         return (net,mask1),(net1,mask1)
#     return ((net,mask1),(net1,mask1), calcnet(net,mask1),calcnet(net1,mask1))

class Network(models.Model):
    # TYPE_OF_NETS= (
    # ('UN','Сеть пользователей'),
    # ('EN','Сеть оборудование'),
    # ('DN','Сеть для распределения'),
    # ('LN','Сеть разделитель'),
    # )
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    ip = models.IPAddressField()
    mask = models.IntegerField(max_length=2)
    vlan = models.ForeignKey(Vlan,null=True,blank=True)
    net_type = models.CharField(_('net_type'),max_length = 2, choices=TYPE_OF_NETS)
    decip = models.PositiveIntegerField(null=True, blank=True)
    segment = models.ForeignKey('users.Segment')

    def clean(self):
        self.ip = dec2ip((ip2dec(self.ip) / pow(2, 32-self.mask))*pow(2, 32-self.mask))
        for item in Network.objects.filter(mask__gt = self.mask):
            if self.net_type != NETWORK_DISTRIB and ip2dec(item.ip) in range(ip2dec(self.ip),ip2dec(self.ip)+pow(2,32-self.mask)-1):
                raise ValidationError('Существует подсеть с меньшей маской')
        for item in Network.objects.filter(mask__lt = self.mask):
            if item.net_type == NETWORK_DISTRIB:
                self.parent = item
            elif ip2dec(self.ip) in range(ip2dec(item.ip),ip2dec(item.ip)+pow(2,32-item.mask)-1):
                raise ValidationError('Существует подсеть с большей маской')

    def save(self, force_insert=False, force_update=False):
        self.decip = sum([int(q) << i * 8 for i, q in enumerate(reversed(self.ip.split(".")))])
        isNew = not self.pk
        super(Network, self).save(force_insert, force_update)
        if isNew and (self.net_type == NETWORK_EQUIP or self.net_type == NETWORK_USERS):
            aList = [ IPAddr(ip = dec2ip(item), net = self, decip = item) for item in range ( self.decip + 1, self.decip + pow(2,32-self.mask) - 1 )]
            IPAddr.objects.bulk_create(aList)

    class Meta:
        verbose_name = u'Сеть'
        verbose_name_plural = u'Сети'
        unique_together = ('ip', 'mask')
        ordering = ['decip']

    def __unicode__(self):
        return "%s/%s" % (self.ip, self.mask)

class IPAddr(models.Model):
    ip = models.IPAddressField(unique=True)
    net = models.ForeignKey(Network)
    decip = models.PositiveIntegerField(null=True, blank=True)

    def clean(self):
#	if IPAddr.objects.filter(net=self.net).count() >= pow(2,32-self.net.mask)-2 :
#		raise ValidationError('Нет свободных адресов в этой подсети')
	self.decip = sum([int(q) << i * 8 for i, q in enumerate(reversed(self.ip.split(".")))])
	if not self.decip in range(self.net.decip+1, self.net.decip+pow(2,32-self.net.mask)-1):
		raise ValidationError('Адрес не пренадлежит выбранной подсети')

#    def save(self, force_insert=False, force_update=False):
#        self.decip = sum([int(q) << i * 8 for i, q in enumerate(reversed(self.ip.split(".")))])
#        super(IPAddr, self).save(force_insert, force_update)

#    def _get_decimal_ip(self):
#        return sum([int(q) << i * 8 for i, q in enumerate(reversed(self.ip.split(".")))])
#    decip = property(_get_decimal_ip)

    class Meta:
        verbose_name = _('IP Address')
        verbose_name_plural = _('IP Addresses')
        ordering = ['decip']

    def __unicode__(self):
        return "%s/%s" % (self.ip, self.net.mask)

# class Device(models.Model):
#     # TYPE_OF_CHECK = (
#     #     ('NC','Не проверять'),
#     #     ('PC','ICMP Проверка'),
#     #     ('SC','SNMP Проверка'),
#     # )
#     title = models.CharField(u'Название', max_length=30)
#     ip = models.OneToOneField(IPAddr, verbose_name=u'IP адрес', 
#         blank=True, null= True)
#     mgmt_vlan = models.ForeignKey(Vlan, related_name='mgmt_vlan',
#         verbose_name=u'VLAN управления', blank=True, null= True)
#     devtype = models.ForeignKey(DevType, verbose_name=u'Модель')
#     is_rooter = models.BooleanField(u'Роутер?')
#     mac = models.CharField(u'MAC адрес', blank=True, null= True, max_length=20)
#     sn = models.CharField(u'Серийный номер', blank=True, 
#                                  null=True, max_length=20)
#     # node = models.ForeignKey(Node, verbose_name=u'Местонахождение')
#     # check_type = models.CharField(u'Тип проверки', max_length = 2, 
#         # choices=TYPE_OF_CHECK)
#     # snmp_community = models.CharField(max_length = 20, blank=True, null= True)
#     last_available = models.DateTimeField(auto_now=False, auto_now_add=False, 
#         blank=True, null=True, verbose_name=u'Последний ответ')

#     class Meta:
#         verbose_name = u'Устройство'
#         verbose_name_plural = u'Устройства'

#     def __unicode__(self):
#         return "%s - %s - %s" % (self.pk, self.title, self.ip)
