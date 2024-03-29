# -*- coding: utf-8 -*- 
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from tinymce.models import HTMLField

MARKS = (
    ('panel-primary', 'Синий'),
    ('panel-success', 'Зеленый'),
    ('panel-info', 'Голубой'),
    ('panel-warning', 'Желтый'),
    ('panel-danger', 'Красный'),
)

TYPE = (
    ('G', 'Обычная'),
    ('C', 'Changelog'),
)

class Note(models.Model):
    title = models.CharField(u'Заголовок', max_length=60 )
    descr = HTMLField(u'Описание')
    marks = models.CharField(u'Цвет', max_length=13, choices = MARKS )
    author = models.ForeignKey(User, verbose_name=u'Автор', blank=True, null= True)
    public = models.BooleanField(u'Для всех',default=False)
    date = models.DateTimeField(default=datetime.now,auto_now_add=True)
    read = models.BooleanField(u'Прочитано',default=False)
    kind = models.CharField(u'Тип заметки', max_length=1, choices = TYPE, default='G')

    class Meta:
        verbose_name = u'Заметка'
        verbose_name_plural = u'Заметки'

    def __unicode__(self):
        return u'[%s] %s - %s' % (self.date.ctime(), self.title, self.author.get_full_name())
