# -*- coding: utf-8 -*- 
from django.db import models
from users.models import Abonent

class Contact(models.Model):
    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент',blank=True, null=True)
    surname = models.CharField(u'Фамилия', max_length=200,default='',blank=True, null=True)
    first_name = models.CharField(u'Имя', max_length=50,default='',blank=True, null=True)
    second_name = models.CharField(u'Отчество', max_length=50,default='',blank=True, null=True)
    position = models.CharField(u'Должность', max_length=70,default='',blank=True, null=True)
    phone = models.CharField(u'Телефон', max_length=200,default='',blank=True, null=True)
    mobile = models.CharField(u'Мобильный',max_length=12,default='',blank=True, null=True)
    fax = models.CharField(u'Факс',max_length=12,default='',blank=True, null=True)
    email = models.CharField(max_length=50,default='',blank=True, null=True)
    address = models.CharField(u'Адрес',max_length=200,default='',blank=True, null=True)
    primary_contact = models.BooleanField(u'Основной контакт', default=False)

    class Meta:
        verbose_name = u'Контакт'
        verbose_name_plural = u'Контакты'

    def _get_full_name(self):
        "Returns the person's full name."
        return '%s %s %s' % (self.first_name, self.second_name, self.surname)
    full_name = property(_get_full_name) 

    def __unicode__(self):
        return self.full_name
