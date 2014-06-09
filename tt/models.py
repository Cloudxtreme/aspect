# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from users.models import Abonent

TT_PREFIX = u'АСП-'

class TroubleTicketCategory(models.Model):
    title = models.CharField(u'Название', max_length=30)
	
    class Meta:
        verbose_name = u'Категория'
        verbose_name_plural = u'Категории'

    def __unicode__(self):
        return u"%s" % (self.title)
		

class TroubleTicket(models.Model):
    def getnumber():
        no = TroubleTicket.objects.count()
        if no == None:
            return '1'
        else:
            return TT_PREFIX + u'%s' % (no + 1)

    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент')
    number = models.CharField(u'Номер', max_length=30, default=getnumber, unique=True)
    performer = models.ForeignKey(User, verbose_name=u'Исполнитель')
    category = models.ForeignKey(TroubleTicketCategory,verbose_name='Тип обращения')
    description = models.CharField(u'Описание', max_length=2000)
    create_date = models.DateTimeField(u'Дата создания', default=datetime.now)
    solve_date = models.DateTimeField(u'Дата закрытия', blank=True, null=True)

    class Meta:
        verbose_name = u'Обращение'
        verbose_name_plural = u'Обращения'
    
    def __unicode__(self):
        return u"%s - %s | %s" % (self.abonent.contract, self.category, self.create_date.ctime())


class TroubleTicketComment(models.Model):
    tt = models.ForeignKey(TroubleTicket,verbose_name=u'Обращение')
    author = models.ForeignKey(User, verbose_name=u'Комментатор')
    comment = models.CharField(u'Описание', max_length=2000)
    create_date = models.DateTimeField(u'Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = u'Комментарий'
        verbose_name_plural = u'Комментарии'

    def __unicode__(self):
        return u"%s | %s" % (self.author, self.create_date.ctime())