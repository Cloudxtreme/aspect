# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
from devices.models import Device

class Log(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь', blank=True, null= True)
    description = models.TextField(u'Описание', blank=True, null=True)
    date = models.DateTimeField(u'Дата', default=datetime.now,auto_now_add=True)
    level = models.CharField(u'Тип запись', max_length=1, choices = settings.TYPE_LOG, default='C')

    class Meta:
        verbose_name = u'Запись Журнала'
        verbose_name_plural = u'Записи Журнала'

    def __unicode__(self):
        return u'[%s] %s - %s' % (self.date.ctime(), self.user.get_full_name(), self.level)

class SomeEntityWithReason(models.Model):
    comment = models.CharField(u'Комментарий', max_length=30, blank=True, null=True)
    attach = models.FileField(u'Приложение', upload_to='user_files', blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата начала')
    laststatus = models.CharField(u'Старый статус', max_length=1, 
        choices=settings.STATUSES, blank=True, null=True)
    newstatus = models.CharField(u'Новый статус', 
        max_length=1, choices=settings.STATUSES)
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