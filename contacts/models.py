# -*- coding: utf-8 -*- 
from django.db import models
# from django.utils.translation import ugettext_lazy as _

class Contact(models.Model):
    surname = models.CharField(u'Фамилия', max_length=50,blank=True, null=True)
    first_name = models.CharField(u'Имя', max_length=50,blank=True, null=True)
    second_name = models.CharField(u'Отчество', max_length=50,blank=True, null=True)
    position = models.CharField(u'Должность', max_length=30,blank=True, null=True)
    phone = models.CharField(u'Телефон', max_length=12,blank=True, null=True)
    mobile = models.CharField(u'Мобильный',max_length=12,blank=True, null=True)
    fax = models.CharField(u'Факс',max_length=12,blank=True, null=True)
    email = models.CharField(max_length=50,blank=True, null=True)
    address = models.CharField(u'Адрес',max_length=200,blank=True, null=True)

    class Meta:
        verbose_name = u'Контакт'
        verbose_name_plural = u'Контакты'

    def _get_full_name(self):
        "Returns the person's full name."
        return '%s %s %s' % (self.first_name, self.second_name, self.surname)
    full_name = property(_get_full_name) 

    def __unicode__(self):
        return self.full_name