# -*- coding: utf-8 -*-
from django.db import models
from vlans.models import IPAddr, Vlan, Location
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from devices.aux import *
from django.conf import settings
from django.core.files.base import ContentFile
import re, uuid, json

# Возвращаем тип устройства по его ОС
def get_devtype(ip):
    device_os = get_dev_os(ip)
    category = 'S'
    if device_os.find('Linux') != -1: # Это Ubiquiti
        _model = get_ubnt_model(ip)
        vendor = 'Ubiquiti'
        if _model: # Это радио
            model = [_model]
            category = 'R'
        else: # А это свитч
            model = ['Tough Switch']
    elif device_os.find('RouterOS') != -1: # Это Mikrotik
        vendor = 'Mikrotik'
        model = re.findall('RouterOS (.*)',device_os)
    elif device_os.find('Cisco') != -1: # Это Cisco
        vendor = 'Cisco'
        model = re.findall('Cisco IOS Software, (.*) Software',device_os)
    elif device_os.find('DES-') != -1: # Это D-Link
        vendor = 'D-Link'
        model = re.findall('(DES-.*) Fast Ethernet Switch',device_os)
    elif device_os.find('ES-2108') != -1: # Это Zyxel ES-2108
        vendor = 'Zyxel'
        model = ['ES-2108']
    elif device_os.find('Fmv') != -1: # Это SNR-pinger
        vendor = 'SNR'
        model = ['Pinger']
        category = 'P'
    else:
        vendor = 'Unknown'
        model = ['Unknown']

    model = model[0] if model else 'Unknown'

    devtype,created = DevType.objects.get_or_create(model=model,
                                    defaults={'vendor': vendor, 
                                                'model' : model, 
                                                'category' : category, })

    return devtype


# Многопоточный 
def get_devince_info(queue):
    for ip in iter(queue.get, None):
        get_devtype(ip)

def scan_network(ip_list):
    queue = Queue()
    threads = [Thread(target=get_devince_info, args=(queue,)) for _ in range(20)]
    for t in threads:
        t.daemon = True
        t.start()

    # Place work in queue
    for site in ip_list: queue.put(site)
    # Put sentinel to signal the end
    for _ in threads: queue.put(None)
    # Wait for completion
    for t in threads: t.join()

def get_config(dev_id):
    try:
        device = Device.objects.get(pk=dev_id)
    except:
        result = False
    
    if device.devtype.vendor == 'Ubiquiti':
        config, result = get_ubnt_cfg(device.ip.ip)
    else:
        result = False

    return config if result == True else ''

class Application(models.Model):
    TYPE_OF_APP = (
        ('R', 'Регламентные работы'),
        ('E', 'Аварийно-восстановительные'),
        ('M', 'Модернизация'),
        ('T', 'Тестирование'),
    )
    type_app = models.CharField(u'Тип работ', max_length = 4, choices=TYPE_OF_APP)
    ipaddr = models.CharField(u'IP устройства', max_length=100)
    description = HTMLField(u'Описание')
    author = models.ForeignKey(User, verbose_name=u'Автор')
    date = models.DateTimeField(auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name = u'Заявка'
        verbose_name_plural = u'Заявки'

    def __unicode__(self):
        return "%s - %s - %s" % (self.date, self.ipaddr, self.author)    

class DevType(models.Model):
    # is_radio = models.BooleanField(u'Радио',default=False)
    vendor = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(u'Тип устройства', max_length = 1, 
                              choices=settings.TYPE_OF_DEVICE, default='S')

    class Meta:
        verbose_name = u'Тип устройства'
        verbose_name_plural = u'Типы устройств'

    def __unicode__(self):
        return "%s - %s" % (self.vendor, self.model)

class Device(models.Model):
    interfaces = models.ManyToManyField('users.Interface', verbose_name=u'Интерфейсы',
                                        blank=True, null=True)
    devtype = models.ForeignKey(DevType, verbose_name=u'Модель')
    mgmt_vlan = models.ForeignKey(Vlan, related_name=u'mgmt_vlan',
        verbose_name=u'VLAN управления', blank=True, null= True)
    comment = HTMLField(u'Комментарий', blank=True, null= True)
    location = models.ForeignKey(Location, blank=True, null=True, 
                                verbose_name=u'Местонахождение')
    router = models.BooleanField(u'Роутер?',default=False)
    # mac = models.CharField(u'MAC адрес', blank=True, null= True, max_length=20) # Надо убрать
    sn = models.CharField(u'Серийный номер', blank=True, 
                                 null=True, max_length=20)
    inv_number = models.CharField(u'Инвентарный номер', blank=True, 
                                 null=True, max_length=20)
    last_available = models.DateTimeField(auto_now=False, auto_now_add=False, 
        blank=True, null=True, verbose_name=u'Последний ответ')
    peer = models.ForeignKey('self',related_name='peer_set', blank=True, null= True,editable=False)
    # Радиопараметры
    # freqs = models.CharField(u'Частоты', default='', max_length=200,editable=False)
    # width = models.CharField(u'Полоса', default='', max_length=2,editable=False)
    # ap = models.BooleanField(u'Access Point', default=False,editable=False)
    # azimuth = models.FloatField(u'Азимут', default=0,editable=False)
    # distance = models.FloatField(u'Дистанция', default=0,editable=False)

    details_map_field = models.TextField(editable=False) # since it will not work anyway
 
    def __init__(self, *args, **kw):
        # here we hold the object. My object is a simple dict, holding some indexed details
        self.details_map = {}
        super(Device, self).__init__(*args, **kw)
        if self.details_map_field:
            # load object from serialized value in field
            self.details_map = json.loads(self.details_map_field)
 
    def save(self, *args, **kw):
        # always add/change values in details_map_field, save() will do the sync with the db
        self.details_map_field = json.dumps(self.details_map)
        super(Device, self).save(*args, **kw)
 
    def ppdetails(self):
        """ Pretty print """
        # this can be used in templates, as an interface to the actual data in field
        dets = json.loads(self.details_map_field)
        if len(dets):
            ret = ['%s: %s' % (k, v) for (k, v) in dets.items()]
            return '\n'.join(ret)
        else:
            return ''

    # Только для SNR получить информаицю о питании
    def get_supply_info(self):
        if self.devtype.category == settings.DEVTYPE_SNR:
            if self.ip:
                voltage = get_snr_voltage(self.ip.ip)
                supply= get_snr_supply(self.ip.ip)
                return voltage,supply

    # Вывести все связи
    def _get_peer(self):
        if self.ip:
            mac = get_ubnt_apmac(self.ip.ip)
            if mac:
                self.ap = False
                peer = Device.objects.filter(interfaces__mac=mac)
                if peer:
                    self.peer = peer[0]
                    self.save()

    # Получить МАС для UBNT
    def _get_macaddr(self):
        if self.ip:
            mac = get_ubnt_macaddr(self.ip.ip)
            if mac:
                iface = self.ip.interface
                iface.mac = mac
                iface.save()

    # Привязать устройство к услуге (Только для физиков)
    def _attach2srv(self):
        if self.ip and self.service_set.all().count()==0:
            devname = get_ubnt_devname(self.ip.ip)
            if devname:
               from users.models import Service
               contract = re.findall('50\d{6}',devname)
               if contract:
                    try:
                        srv = Service.objects.get(abon__contract=contract[0])
                    except:
                        pass
                    else:
                        srv.device = self
                        srv.save()

    # Получить модель устройства
    def _get_model(self):
        if self.ip:
            self.devtype=get_devtype(self.ip.ip)
            self.save()

    # Выдаем первый IP-адрес
    def _get_main_ip(self):
        if self.interfaces.count():
            return self.interfaces.all().first().ip
        else:
            return None

    # Заполняем параметры азимута и дистанции
    # def _refresh_azimuth(self):
    #     if self.location:
    #         azimuth_list =[]
    #         distance_list = []
    #         for peer in self.peers:
    #             if peer.location:
    #                 azimuth,distance = azimuth_distance(self.location.geolocation, peer.location.geolocation)
    #                 azimuth_list.append(azimuth)
    #                 distance_list.append(distance)
    #         self.azimuth, self.distance = sum(azimuth_list)/len(azimuth_list), max(distance_list)
    #         self.save()

    def _get_peers(self):
        if self.peer:
            # return self.peer
            return Device.objects.filter(pk=self.peer.pk)
        else:
            return self.peer_set.all()

    # Только сохранить конфиг
    def _save_config(self,text_config):
        filename = '%s.cfg' % uuid.uuid4().hex
        config = Config()
        config.device = self
        config.attach.save(filename,ContentFile(text_config))
        config.save()
        return config.pk

    # Получить и сохранить конфиг
    # def _get_config(self):
    #     result = False
    #     if self.devtype.vendor == 'Ubiquiti':
    #         config, success = get_ubnt_cfg(self.ip.ip)
    #         if success: 
    #             result = bool(self._save_config(config))
    #     return result

    # Только для UBNT получение, анализ и сохранение конфига
    def _get_config(self):    
    # def _refresh_radio(self):
        result = False
        if self.devtype.vendor == 'Ubiquiti':
            config, success = get_ubnt_cfg(self.ip.ip)
            if success:
                result = bool(self._save_config(config))
                if self.devtype.category == settings.DEVTYPE_RADIO:
                    self.details_map['freqs'] = ', '.join(get_ubnt_freq(config))
                    self.details_map['width'] = get_ubnt_width(config)
                    self.details_map['mode'] = 'Access Point' if get_ubnt_ap(config) else 'Station'
                    self.save()

        return result

    ip = property(_get_main_ip)
    peers = property(_get_peers)

    class Meta:
        verbose_name = u'Устройство'
        verbose_name_plural = u'Устройства'

    def __unicode__(self):
        return u"%s - %s" % (self.devtype, self.ip)

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
        return u"[%s] %s - is now %s " % (self.date, self.device, state)

class Config(models.Model):
    device = models.ForeignKey(Device,verbose_name=u'Устройство')
    attach = models.FileField(u'Приложение', upload_to='configs')
    date = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        verbose_name = u'Конфиг'
        verbose_name_plural = u'Конфиги'
        ordering = ['-date']

    def __unicode__(self):
        return u"[%s] - %s" % (self.date, self.device)