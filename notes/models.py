# -*- coding: utf-8 -*- 
from django.db import models
# from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

MARKS = (
    ('panel-primary', 'Синий'),
    ('panel-success', 'Зеленый'),
    ('panel-info', 'Голубой'),
    ('panel-warning', 'Желтый'),
    ('panel-danger', 'Красный'),
)

class Note(models.Model):
    title = models.CharField(u'Заголовок', max_length=20 )
    descr = models.CharField(u'Описание', max_length=2000 )
    marks = models.CharField(u'Отметка', max_length=13, choices = MARKS )
    author = models.ForeignKey(User, verbose_name=u'Автор', blank=True, null= True)
    public = models.BooleanField(u'Для всех',default=False)

    class Meta:
        verbose_name = u'Заметка'
        verbose_name_plural = u'Заметки'

    def __unicode__(self):
        return self.title
