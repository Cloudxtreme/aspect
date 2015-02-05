# -*- coding: utf-8 -*- 
from django.db import models
from users.models import Abonent

class Contact(models.Model):
    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент',blank=True, null=True)
    surname = models.CharField(u'Фамилия', max_length=200,default='')
    first_name = models.CharField(u'Имя', max_length=50,default='')
    second_name = models.CharField(u'Отчество', max_length=50,default='')
    position = models.CharField(u'Должность', max_length=70,default='')
    phone = models.CharField(u'Телефон', max_length=200,default='')
    mobile = models.CharField(u'Мобильный',max_length=12,default='')
    fax = models.CharField(u'Факс',max_length=12,default='')
    email = models.CharField(max_length=50,default='')
    address = models.CharField(u'Адрес',max_length=200,default='')
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
