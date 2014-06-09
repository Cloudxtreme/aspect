# -*- coding: utf-8 -*- 
from django.db import models
from django.utils.translation import ugettext_lazy as _

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

    class Meta:
        verbose_name = u'Заметка'
        verbose_name_plural = u'Заметки'

    def __unicode__(self):
        return self.title
