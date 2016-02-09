# -*- coding: utf-8 -*- 
from django.db import models
from django.core.exceptions import ValidationError
from vlans.fields import LocationField
from devices.aux import ip2dec,dec2ip
# from users.models import Service
# from vlans.aux import get_profit_by_bs
# import vlans.aux
from django.db.models import Sum

TYPE_OF_OBJECTS = (
    ('C', 'Клиент'),
    ('B', 'Базовая Станция'),
    ('PB','Возможная БС'),
    ('CP','Точка раздачи'),
)

NETWORK_USERS = 'UN'
NETWORK_EQUIP = 'EN'
NETWORK_DISTRIB = 'DN'
NETWORK_LIMITER = 'LN'
NETWORK_PTP = 'PN'

TYPE_OF_NETS = (
    (NETWORK_USERS,'Сеть пользователей'),
    (NETWORK_EQUIP,'Сеть оборудование'),
    (NETWORK_DISTRIB,'Сеть для распределения'),
    (NETWORK_LIMITER,'Сеть разделитель'),
    (NETWORK_PTP,'Сеть /32'),
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

class Rent(models.Model):
    title = models.CharField(u'Название',max_length=100)
    cost = models.FloatField(u'Арендная плата',default=0)
    
    class Meta:
        verbose_name = u'Тариф аренды'
        verbose_name_plural = u'Тарифы аренды'

    def __unicode__(self):
        return u"%s - %s руб/мес" % (self.title, self.cost)

class Location(models.Model):
    title = models.CharField(u'Название', blank=True, null= True, max_length=100)
    address = models.CharField(u'Адрес', blank=True, null= True, max_length=300)
    bs_type = models.CharField(u'Тип', max_length = 2, 
                               choices=TYPE_OF_OBJECTS)
    comment  = models.CharField(u'Комментарий', max_length=300, blank=True, null=True, default='')
    rent = models.ForeignKey(Rent, null=True, blank=True,verbose_name=u'Тариф аренды')
    geolocation = LocationField(u'Карта', max_length=100, blank=True, null=True)
    # geolocation = models.CharField(u'Карта', max_length=100, blank=True, null=True) # Заглушка для South
   
    @property
    def get_geolocation(self):
        if self.geolocation:
            return self.geolocation.split(',')

    def get_profit(self):
        if self.bs_type in ['B','CP']:
            from users.models import Service
            srv_list = Service.objects.filter(device__peer__location__pk=self.pk)|\
                       Service.objects.filter(device__location__pk=self.pk)
            # active_srv_list = srv_list.filter(status=settings.STATUS_ACTIVE)

            profit = srv_list.aggregate(Sum('plan__price'))['plan__price__sum'] or 0
            # active_profit = active_srv_list.aggregate(Sum('plan__price'))['plan__price__sum']

            # satellite_list =[]
            satellite_profit = 0

            if self.bs_type == 'B':
                for d in self.device_set.all():
                    for p in d.peers:
                        if p.location:
                            if p.location.bs_type == 'CP':
                                satellite_profit += p.location.get_profit()

                                # satellite_profit += satellite.get_profit()
                                # satellite_list.append(sat_id)
                        # else:
                    #     print p # Выводим устройства не привязанные к БС
            # print 'БС: [%s] - список пересков: %s' % (self.pk, satellite_list)
            # for sat_id in satellite_list:
            #     satellite = Location.objects.get(sat_id)
            #     satellite_profit += satellite.get_profit()

            # print satellite_list

            return profit + satellite_profit 

    class Meta:
        verbose_name = u'Местонахождение'
        verbose_name_plural = u'Местонахождения'
        ordering = ['title']

    def __unicode__(self):
        return "[%s] %s" % (self.pk, self.address)

class Node(models.Model):
    title  = models.CharField(max_length=100)
    latlng = models.CharField(u'lat/lon', blank=True, max_length=300)
    bs_type = models.CharField(u'Тип БС', max_length = 2, 
                               choices=TYPE_OF_OBJECTS)

    class Meta:
        verbose_name = u'Адрес'
        verbose_name_plural = u'Адреса'
        ordering = ['title']

    def __unicode__(self):
        return "%s - %s - %s" % (self.pk, self.title, self.bs_type)

class Network(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    ip = models.IPAddressField(u'Адрес сети')
    mask = models.IntegerField(u'Маска',max_length=2)
    vlan = models.ForeignKey(Vlan,null=True,blank=True)
    net_type = models.CharField(u'Тип сети',max_length = 2, choices=TYPE_OF_NETS)
    decip = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(u'Описание',max_length=200, blank=True, null=True)
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

class TrafRecord(models.Model):
    ip = models.ForeignKey(IPAddr)
    octets = models.BigIntegerField(u'Bytes')
    interval = models.PositiveIntegerField(u'Интервал в сек',default=300)
    inbound = models.BooleanField(u'Входящий',default=True)
    time = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        verbose_name = u'Трафик'
        verbose_name_plural = u'Трафик'
        ordering = ['time']

    def __unicode__(self):
        return "%s - %s - %s" % (self.time, self.ip, self.octets)