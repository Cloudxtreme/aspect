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

class EmailMessage(models.Model):
    abonent = models.ForeignKey('users.Abonent', verbose_name=u'Абонент', blank=True, null=True)
    destination = models.CharField(u'Получатель', max_length=70)
    subject = models.CharField(u'Тема', max_length=70)
    content = models.CharField(u'Сообщение', max_length=200)
    date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата')
    sent = models.BooleanField(u'Отправлено', default=False)
    group_id = models.IntegerField(u'Номер групповой рассылки', default=0, blank=True, null=True)

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
                conn.sendmail(settings.EMAIL_SENDER, self.destination, msg.as_string())
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