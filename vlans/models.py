# -*- coding: utf-8 -*- 
from django.db import models
# from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from vlans.fields import LocationField

# Create your models here.

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
    title = models.CharField(u'Название',max_length=30)
    number = models.IntegerField(u'Номер', unique=True)
    description = models.CharField(u'Описание',max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = u'Vlan'
        verbose_name_plural = u'Vlans'
        ordering = ['number']

    def __unicode__(self):
        return "%s - %s" % (self.number, self.description)

class Location(models.Model):
    address = models.CharField(u'Адрес', blank=True, null= True, max_length=100)
    # lat = models.FloatField(u'Широта', blank=True, null=True)
    # lon = models.FloatField(u'Долгота', blank=True, null=True)
    bs_type = models.CharField(u'Тип', max_length = 2, 
                               choices=TYPE_OF_OBJECTS)
    comment  = models.CharField(u'Комментарий', max_length=300, blank=True, null=True, default='')
    geolocation = LocationField(u'Карта', max_length=100, blank=True, null=True)
    # geolocation = models.CharField(u'Карта', max_length=100, blank=True, null=True) # Заглушка для South
   
    @property
    def get_geolocation(self):
        if self.geolocation:
            return self.geolocation.split(',')

    class Meta:
        verbose_name = u'Местонахождение'
        verbose_name_plural = u'Местонахождения'

    def __unicode__(self):
        return "%s" % (self.address)

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

class Network(models.Model):
    # TYPE_OF_NETS= (
    # ('UN','Сеть пользователей'),
    # ('EN','Сеть оборудование'),
    # ('DN','Сеть для распределения'),
    # ('LN','Сеть разделитель'),
    # )
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    ip = models.IPAddressField(u'Адрес сети')
    mask = models.IntegerField(u'Маска',max_length=2)
    vlan = models.ForeignKey(Vlan,null=True,blank=True)
    net_type = models.CharField(u'Тип сети',max_length = 2, choices=TYPE_OF_NETS)
    decip = models.PositiveIntegerField(null=True, blank=True)
    segment = models.ForeignKey('users.Segment')
    in_dhcpd = models.BooleanField(u'Включать в DHCP',default=False)

    def clean(self):
        self.ip = dec2ip((ip2dec(self.ip) / pow(2, 32-self.mask))*pow(2, 32-self.mask))
        for item in Network.objects.filter(mask__gt = self.mask):
            if self.net_type != NETWORK_DISTRIB and ip2dec(item.ip) in range(ip2dec(self.ip),ip2dec(self.ip)+pow(2,32-self.mask)-1):
                raise ValidationError('Существует подсеть с меньшей маской')
        for item in Network.objects.filter(mask__lt = self.mask):
            if item.net_type == NETWORK_DISTRIB and ip2dec(self.ip) in range(item.decip, item.decip + pow(2,32-item.mask)-1):
            # ip2dec(item.ip) in range(ip2dec(self.ip),ip2dec(self.ip)+pow(2,32-self.mask)-1):
                self.parent = item
            elif item.net_type != NETWORK_DISTRIB and \
            (ip2dec(self.ip) in range(item.decip,item.decip+pow(2,32-item.mask)-1) or \
                ip2dec(self.ip)+pow(2,32-self.mask)-1 in range(item.decip,item.decip+pow(2,32-item.mask)-1)):
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
        verbose_name = u'IP Адрес'
        verbose_name_plural = u'IP Адреса'
        ordering = ['decip']

    def __unicode__(self):
        return "%s/%s" % (self.ip, self.net.mask)