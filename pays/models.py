# -*- coding: utf-8 -*- 
from django.db import models
from django.db.models import F
from users.models import Abonent, Service
# import users
from django.contrib.auth.models import User
from datetime import datetime
from notice.models import AbonentEvent
# from django.utils import timezone

PAYS_PREFIX = u''
WRITEOFF_PREFIX = u''

class PaymentSystem(models.Model):
    title = models.CharField(max_length=200)
    stat = models.BooleanField(u'Учитывать в статистике')

    class Meta:
        verbose_name = u'Платежная система'
        verbose_name_plural = u'Платежные системы'

    def __unicode__(self):
        return self.title

class WriteOffType(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name = u'Тип списания'
        verbose_name_plural = u'Типы списаний'

    def __unicode__(self):
        return self.title        

class PromisedPays(models.Model):
    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент')
    summ = models.FloatField(u'Сумма')
    user = models.ForeignKey(User, verbose_name=u'Пользователь', blank=True, null= True)
    datestart = models.DateTimeField(default=datetime.now, verbose_name=u'Дата начала')
    datefinish = models.DateTimeField(verbose_name=u'Дата завершения', blank=True, null= True)
    comment = models.CharField(u'Комментарии', blank=True, null= True, max_length=200)
    pay_onaccount = models.BooleanField(default=False, editable=False)
    repaid = models.BooleanField(u'Оплачен', default=False)

    def is_finished(self):
        return (not self.pay_onaccount and self.datefinish > datetime.now())

    def close(self):
        if self.pay_onaccount:
            Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') - self.summ)
            Abonent.objects.get(pk=self.abonent.pk).check_status('Обещанный платеж закончен')
            self.pay_onaccount = False
        if not self.datefinish:
            self.datefinish = datetime.now()
        if self.datefinish.replace(tzinfo=None) > datetime.now():
            self.datefinish = datetime.now()
        super(PromisedPays, self).save()

    def save(self, *args, **kwargs):
        if not self.pk:
            Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') + self.summ)
            Abonent.objects.get(pk=self.abonent.pk).check_status('Обещанный платеж зачислен')
            self.pay_onaccount = True
        else:
            lastsumm = PromisedPays.objects.get(pk=self.pk).summ
            if lastsumm != self.summ:
                Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') - lastsumm)
                Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') + self.summ)
                Abonent.objects.get(pk=self.abonent.pk).check_status('Изменена сумма обещанного платежа')

        super(PromisedPays, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Обещанный платеж'
        verbose_name_plural = u'Обещанные платежи'

    def __unicode__(self):
        return u"[%s], %s руб., %s - %s" % (self.abonent.contract, self.summ, self.datestart.ctime(), self.datefinish.ctime() )


class WriteOff(models.Model):
    def getnumber():
        # pass
        # no = WriteOff.objects.filter(valid=True).count()
        no = WriteOff.objects.all().order_by("-id")[0].id or 1
        return WRITEOFF_PREFIX + u'%06d' % (no + 1)

    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент')
    service = models.ForeignKey(Service, verbose_name=u'Услуга', blank=True, null=True)
    wot = models.ForeignKey(WriteOffType, verbose_name=u'Тип списания')
    summ = models.FloatField(u'Сумма')
    date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата')
    user = models.ForeignKey(User, verbose_name=u'Пользователь', blank=True, null= True)
    number = models.CharField(u'Номер документа', unique=True, default=getnumber, max_length=20)
    valid = models.BooleanField(u'Действителен', default=True)
    comment = models.CharField(u'Комментарии', blank=True, null= True, max_length=200)
    newbalance = models.FloatField(u'Новый баланс',default=0)

    def save(self, *args, **kwargs):
        isNew = not self.pk
        super(WriteOff, self).save(*args, **kwargs)
        if isNew: 
            if self.number == '':
                self.number = self.pk
                super(WriteOff, self).save(*args, **kwargs)
            Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') - self.summ)
            abonent = Abonent.objects.get(pk=self.abonent.pk)
            abonent.check_status(reason='Списание средств')
            self.newbalance = abonent.balance
            super(WriteOff, self).save(*args, **kwargs)
            try:
                abonentevent = AbonentEvent.objects.get(pk=2) #pk=2 Списание средств
            except Exception, e:
                pass
            else:
                extra_keys = { 'summa' : self.summ }
                abonentevent.generate_messages([self.abonent],extra_keys)

            # Уведомление о списании средств со счета
            # if abonent.notice_email and self.summ > 0:
            #     email = EmailMessage(abonent=abonent, destination = abonent.notice_email, subject = 'Списание средств', content = u'С вашего счета списано: %s руб. Теперь на вашем счету %s руб.' % (self.summ, abonent.balance) )
            #     email.save()      
            
            
    def delete(self, *args, **kwargs):
        Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') + self.summ)
        self.valid = False
        self.save()
    
    class Meta:
        verbose_name = u'Списание'
        verbose_name_plural = u'Списания'

    def __unicode__(self):
        return u"%s, %s,  %s руб., %s" % (self.abonent.contract, self.wot,  self.summ, self.date.ctime())

class PaymentFilterManager(models.Manager):
    def filter_list(self,utype=[],top=[],datestart=None,datefinish=None):
        payment_list = super(PaymentFilterManager, self).get_query_set()
        payment_list = payment_list.filter(date__range=[datestart, datefinish],valid=True)
        if top:
            payment_list = payment_list.filter(top__in=top)
        if utype:
            payment_list = payment_list.filter(abonent__utype__in=utype)
        return payment_list.order_by('-date')

    def get_query_set(self):
        return super(PaymentFilterManager, self).get_query_set()
        
class Payment(models.Model):
    def getnumber():
        # pass
        # no = Payment.objects.filter(valid=True).count()
        no = Payment.objects.all().order_by("-id")[0].id or 1
        return PAYS_PREFIX + u'%06d' % (no + 1)
    
    # abon = models.ForeignKey(Abonent, verbose_name=u'Абонент',related_name='old_abonent')
    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент',related_name='abonent')
    top = models.ForeignKey(PaymentSystem, verbose_name=u'Платежная система')
    # sum = models.FloatField(u'Сумма')
    summ = models.FloatField(u'Сумма',default=0)
    date = models.DateTimeField(default=datetime.now, verbose_name=u'Дата')
    user = models.ForeignKey(User, verbose_name=u'Пользователь', blank=True, null= True)
    num = models.CharField(u'Номер документа', max_length=30, unique=True, default=getnumber)
    valid = models.BooleanField(u'Действителен', default=True)
    newbalance = models.FloatField(u'Новый баланс',default=0)
    objects = models.Manager()
    obj = PaymentFilterManager()

    def save(self, *args, **kwargs):
        isNew = not self.pk
        if not isNew:
            diff = Payment.objects.get(pk=self.pk).summ - self.summ
            Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') - diff)
            abonent = Abonent.objects.get(pk=self.abonent.pk)
            abonent.check_status(reason='Изменен размер платежа')
        if self.summ == 0:
            self.valid = False
        super(Payment, self).save(*args, **kwargs)
        if isNew: 
            if self.num == '':
                self.num = self.pk
                super(Payment, self).save(*args, **kwargs)

            PromisedPays.objects.filter(abonent__pk=self.abonent.pk, pay_onaccount=True).update(repaid=True)
            Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') + self.summ)
            abonent = Abonent.objects.get(pk=self.abonent.pk)
            abonent.check_status(reason='Зачисление средств')
            self.newbalance = abonent.balance
            super(Payment, self).save(*args, **kwargs)
            try:
                abonentevent = AbonentEvent.objects.get(pk=1) #pk=1 Пополнение счета
            except Exception, e:
                pass
            else:
                extra_keys = { 'summa' : self.summ, 'balance' : round(abonent.balance,2) }
                abonentevent.generate_messages([self.abonent],extra_keys)
            
    def delete(self, *args, **kwargs):
        # self.abonent.balance = F('balance') - self.summ
        Abonent.objects.filter(pk=self.abonent.pk).update(balance=F('balance') - self.summ)
        # self.abonent.balance -= self.summ
        # self.abonent.save()
        self.valid = False
        self.save()
        # super(Payment, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = u'Платеж'
        verbose_name_plural = u'Платежи'

    def __unicode__(self):
        return u"%s, %s,  %s руб., %s" % (self.abonent.contract, self.top,  self.summ, self.date.ctime())