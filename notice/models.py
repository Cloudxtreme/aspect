# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
# from django.contrib.auth.models import User
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText
from django.conf import settings
# from users.models import Abonent
import sys
import os
import re

# SMTPserver = 'smtp.yandex.ru'
# sender =     'albeon@ptls.ru'
# USERNAME = "albeon@ptls.ru"
# PASSWORD = "yfpfgbcm"
# destination = ['d.sitnikov@albeon.ru']

# content="""\
# Test message
# """

# subject="Sent from Python"
# class GroupEmailMessage(models.Model):
#     PERIOD = (
#         ('0', 'Не повторять'),
#         ('1', 'Ежедневно'),
#         ('2', 'Еженедельно'),
#         ('3', 'Ежемесячно'),
#     )
#     #new_service.datestart = datetime.date.today() + datetime.timedelta(days=1)
#     subject = models.CharField(u'Тема', max_length=70)
#     content = models.CharField(u'Сообщение', max_length=500)    
#     date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата рассылки')
#     permited = models.BooleanField(u'Разрешено к отправке', default=False)
#     done = models.BooleanField(u'Выполнена', default=False)
#     periodic = models.CharField(u'Повторять', max_length=1, choices=PERIOD)

    # def create_messages(self):
    #     for item in abonent_list:
    #             abonent = Abonent.objects.get(pk=item)
    #             # здесь подставновка значения поля вместо его имени!
    #             filtered_content = self.content
    #             for field in abonent.__dict__.keys():
    #                 filtered_content=filtered_content.replace('[%s]' % field, '%s' % abonent.__dict__[field] )

    #             if  abonent.notice_email:
    #                 eList += [EmailMessage(abonent = abonent,
    #                                        destination = abonent.notice_email,
    #                                        subject=self.subject,
    #                                        content=filtered_content,
    #                                        date=self.date,
    #                                        group=self
    #                                        group_id=1 + (EmailMessage.objects.all().aggregate(Max('group_id'))['group_id__max'] or 0) )]
    #         EmailMessage.objects.bulk_create(eList)


class EmailMessage(models.Model):
    abonent = models.ForeignKey('users.Abonent', verbose_name=u'Абонент', blank=True, null=True)
    destination = models.CharField(u'Получатель', max_length=70)
    subject = models.CharField(u'Тема', max_length=70)
    content = models.CharField(u'Сообщение', max_length=500)
    date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата рассылки')
    sent = models.BooleanField(u'Отправлено', default=False)
    # group = models.ForeignKey(GroupEmailMessage, verbose_name=u'Групповая рассылка', blank=True, null=True)
    group_id = models.IntegerField(u'Номер групповой рассылки', default=0, blank=True, null=True) # Оставлено для совместимости

    def sendit(self):
        text_subtype = 'plain' # typical values for text_subtype are plain, html, xml
        try:
            msg = MIMEText(self.content, text_subtype, 'utf-8')
            msg['Subject'] = self.subject
            msg['From']    = settings.EMAIL_SENDER # some SMTP servers will do this automatically, not all

            conn = SMTP(settings.EMAIL_SERVER)
            conn.set_debuglevel(False)
            conn.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            try:
                conn.sendmail(settings.EMAIL_SENDER, [self.destination,'test-email@ptls.ru'], msg.as_string())
            finally:
                conn.close()
                self.sent = True
                self.save()

        except Exception, exc:
            sys.exit( "mail failed; %s" % str(exc) ) # give a error message

    class Meta:
        verbose_name = u'EMail Сообщение'
        verbose_name_plural = u'EMail Сообщения'

    def __unicode__(self):
        return u"%s [%s]" % ( self.date.ctime(), self.destination )