# -*- coding: utf-8 -*-
from django.db import models
from devices.models import Device
from datetime import datetime
# import datetime

# Create your models here.
STATUS_ACTIVE = 'A'
STATUS_OUT_OF_BALANCE = 'N'
STATUS_NEW = 'W'
PAY_CREDIT = 'O'
PAY_POST = 'R'

STATUSES = (
    (STATUS_NEW, 'Новый'),
    (STATUS_ACTIVE, 'Активный'),
    ('S', 'Приостановлен'),
    (STATUS_OUT_OF_BALANCE, 'Отключен за неуплату'),
    ('D', 'Архив'),
)

class DeviceStatusEntry(models.Model):
    device = models.ForeignKey(Device, verbose_name=u'Устройство')
    status = models.CharField(u'Новый статус', max_length=1, 
        choices=( ('A', 'Доступен'),('N','Недоступен') ))
    date = models.DateTimeField(auto_now_add=True)


class SomeEntityWithReason(models.Model):
    comment = models.CharField(u'Комментарий', max_length=30, blank=True, null=True)
    attach = models.FileField(u'Приложение', upload_to='user_files', blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата начала')
    laststatus = models.CharField(u'Старый статус', max_length=1, 
        choices=STATUSES, blank=True, null=True)
    newstatus = models.CharField(u'Новый статус', 
        max_length=1, choices=STATUSES)
    done = models.BooleanField(u'Исполнен', default=False)
    successfully = models.BooleanField(u'Успешно', default=False)

    class Meta:
        abstract = True


class ServiceStatusChanges(SomeEntityWithReason):
    service = models.ForeignKey('users.Service', verbose_name=u'Услуга')
    # datetimefinish = models.DateTimeField(auto_now=False,
        # auto_now_add=False, blank=True, null=True, verbose_name=u'Дата окончания')
    #reason = models.ForeignKey('users.Reason', verbose_name=u'Основание')
    
    class Meta:
        verbose_name = u'Изменение статуса услуги'
        verbose_name_plural = u'Изменение статусов услуг'   
        
    def __unicode__(self):
        return '[%s] %s %s %s' % (self.service.pk, self.laststatus, self.newstatus, self.date)
    
class AbonentStatusChanges(SomeEntityWithReason):
    abonent = models.ForeignKey('users.Abonent', verbose_name=u'Абонент')
    #reason = models.ForeignKey('users.Reason', verbose_name=u'Основание')
    
    class Meta:
        verbose_name = u'Изменение статуса абонента'
        verbose_name_plural = u'Изменение статусов абонентов'  

    def __unicode__(self):
        return '[%s] %s : %s -> %s ' % (self.date, self.abonent.contract, self.get_laststatus_display(),self.get_newstatus_display())            
#        return '%s %s %s %s' % (self.abonent.title, self.get_laststatus_display(), self.get_newstatus_display(), self.datetime )        