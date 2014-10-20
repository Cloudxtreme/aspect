# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
# from django.contrib.auth.models import User
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
from email.utils import formatdate
from email import Encoders
from tinymce.models import HTMLField
from django.conf import settings
from users.models import Detail
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

class TemplateMessage(models.Model):
    title = models.CharField(u'Название', max_length=300)
    subject = models.CharField(u'Тема', max_length=300)
    content = HTMLField(u'Сообщение')
    
    class Meta:
        verbose_name = u'Шаблон'
        verbose_name_plural = u'Шаблоны'

    def __unicode__(self):
        return u'%s' % (self.title)

class AbonentEvent(models.Model):
    title = models.CharField(u'Название', max_length=300, editable=True)
    template_fiz = models.ForeignKey(TemplateMessage, verbose_name=u'Шаблон сообщения для физ. лиц', related_name='template_fiz', blank=True, null=True)
    template_ur = models.ForeignKey(TemplateMessage, verbose_name=u'Шаблон сообщения для организаций', related_name='template_ur', blank=True, null=True)

    def generate_messages(self,abonent_list,extra_keys):
        eList = []
        for abonent in abonent_list:
           if  abonent.notice_email:
                # Определяем какой шаблон выбирать
                if abonent.utype == settings.U_TYPE_UR:
                    if not self.template_ur:
                        break
                    template = self.template_ur
                    filtered_content = template.content.replace('[title]','%s' % Detail.objects.get(abonent=abonent).title)
                    # filtered_content = template.content
                else:
                    if not self.template_fiz:
                        break
                    template = self.template_fiz
                    filtered_content = template.content
               
                # здесь подставновка значения поля вместо его имени!
                for field in abonent.__dict__.keys():
                    filtered_content=filtered_content.replace('[%s]' % field, '%s' % abonent.__dict__[field] )
                # а здесь дополнительные ключи, например [summa] сумма платежа
                for value in extra_keys.keys():
                    filtered_content = filtered_content.replace('[%s]' % value, '%s' % extra_keys[value])

                # формируем список сообщений
                eList += [EmailMessage(abonent = abonent,
                                       destination = abonent.notice_email,
                                       subject=template.subject,
                                       content=filtered_content,
                                       date=datetime.now(),
                         )]
        EmailMessage.objects.bulk_create(eList)

    class Meta:
        verbose_name = u'Пользовательское событие'
        verbose_name_plural = u'Пользовательские События'

    def __unicode__(self):
        return u'%s' % (self.title,)    

class EmailMessage(models.Model):
    abonent = models.ForeignKey('users.Abonent', verbose_name=u'Абонент', blank=True, null=True)
    destination = models.CharField(u'Получатель', max_length=70)
    subject = models.CharField(u'Тема', max_length=70)
    content = HTMLField(u'Сообщение')
    date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата рассылки')
    sent = models.BooleanField(u'Отправлено', default=False)
    attach = models.FileField(upload_to='invoices',blank=True, null=True)

    def sendit(self):
        text_subtype = 'html' # typical values for text_subtype are plain, html, xml
        try:
            # msg = MIMEText(self.content, text_subtype, 'utf-8')
            msg = MIMEMultipart()
            msg['Subject'] = self.subject
            msg['From']    = settings.EMAIL_SENDER # some SMTP servers will do this automatically, not all
            msg['Message-Id'] = make_msgid()
            msg['Date'] = formatdate(localtime=True)
            msg.attach(MIMEText(self.content, text_subtype, 'utf-8'))

            if self.attach:
                filename = self.attach.file.name
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(filename,"rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(filename))
                msg.attach(part)

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
        ordering = ['sent','-pk']

    def __unicode__(self):
        return u"%s [%s]" % ( self.date.ctime(), self.destination )