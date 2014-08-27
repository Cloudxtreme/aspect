# -*- coding: utf-8 -*-
from django.db import models
from vlans.models import IPAddr, Vlan, Node 
from devices.models import Device
# from contacts.models import Contact
from journaling.models import AbonentStatusChanges, ServiceStatusChanges
from django.core.validators import RegexValidator
from users.fields import JSONField
from django.contrib.auth.models import User
import datetime
import calendar
import pays.models
from django.conf import settings

class Segment(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name = u'Сегмент'
        verbose_name_plural = u'Сегменты'

    def __unicode__(self):
        return self.title

class TypeOfService(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name = u'Тип услуги'
        verbose_name_plural = u'Типы услуг'

    def __unicode__(self):
        return self.title

class Plan(models.Model):
    title = models.CharField(max_length=200)
    tos = models.ForeignKey(TypeOfService,verbose_name=u'Группа тарифа')
    segment = models.ManyToManyField(Segment,verbose_name=u'Сегмент')
    speed_in = models.PositiveIntegerField(blank=True, null=True)
    speed_out = models.PositiveIntegerField(blank=True, null=True)
    comment = models.CharField(max_length=200,blank=True, null=True)
    price = models.FloatField(u'Абон. плата')
    install_price = models.FloatField(u'Стоимость подключения',default=0)
    visible = models.BooleanField(u'Видимость',default=True)

    class Meta:
        verbose_name = u'Тарифный план'
        verbose_name_plural = u'Тарифные планы'

    def __unicode__(self):
        return u"%s %s - %s руб/мес" % (self.tos, self.title, self.price)

def has_changed(instance, field):
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.filter(pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value

class Agent(models.Model):
    title = models.CharField(u'Название', max_length=70)
    agent_id = models.CharField(u'ID', max_length=20)
    
    class Meta:
        verbose_name = u'Агент'
        verbose_name_plural = u'Агенты'       
        
    def __unicode__(self):
        return "%s - %s" % (self.agent_id, self.title)

class AbonentFilterManager(models.Manager):
    def filter_list(self,title='',contract='',status=[],utype=[],tos=[],is_credit=[],balance_lt=None,balance_gt=None):
        abonent_list = super(AbonentFilterManager, self).get_query_set()
        if title:
            abonent_list = abonent_list.filter(title__icontains=title)
        if contract:
            abonent_list = abonent_list.filter(contract__icontains=contract)            
        if status:
            abonent_list = abonent_list.filter(status__in=status)
        if utype:
            abonent_list = abonent_list.filter(utype__in=utype)
        if tos:
            abonent_list = abonent_list.filter(service__in=Service.objects.filter(tos__in=tos)).distinct()
        if is_credit:
            abonent_list = abonent_list.filter(is_credit__in=is_credit)
        if balance_lt or balance_lt==0:
            abonent_list = abonent_list.filter(balance__lt=balance_lt)
        if balance_gt or balance_gt==0:
            abonent_list = abonent_list.filter(balance__gte=balance_gt)
        return abonent_list

    def get_query_set(self):
        return super(AbonentFilterManager, self).get_query_set()

class Abonent(models.Model):
    title = models.CharField(u'Название', max_length=70)
    contract = models.CharField(u'Номер договора',max_length=15,blank=True, null=True)
    status = models.CharField(u'Статус',max_length=1, choices=settings.STATUSES, default=settings.STATUS_NEW)
    utype = models.CharField(u'Тип абонента', max_length=1, choices=settings.U_TYPE)
    is_credit = models.CharField(u'Тип оплаты', max_length=1, choices=settings.PAYTYPE)
    agent = models.ForeignKey(Agent,verbose_name=u'Агент', blank=True, null=True)
    balance = models.FloatField(u'Баланс', default = 0)
    reserve = models.FloatField(u'Резерв', default = 0)
    rest = models.FloatField(u'Остаток', default = 0)
    notice_email = models.CharField(u'Email для уведомлений', max_length=70, blank=True, null=True)
    notice_mobile = models.CharField(u'Телефон для уведомлений', max_length=13, blank=True, null=True)
    objects = models.Manager()
    obj = AbonentFilterManager()

    # def filter_list(self,status,utype,is_credit,balance_lt,balance_gt):
    #     abonent_list = Abonent.objects.all()
    #     if status:
    #         abonent_list = abonent_list.filter(status__in=status)
    #     if utype:
    #         abonent_list = abonent_list.filter(utype__in=utype)
    #     if is_credit:
    #         abonent_list = abonent_list.filter(is_credit__in=is_credit)
    #     if balance_lt or balance_lt==0:
    #         abonent_list = abonent_list.filter(balance__lte=balance_lt)
    #     if balance_gt or balance_gt==0:
    #         abonent_list = abonent_list.filter(balance__gte=balance_gt)
    #     return abonent_list

    def set_changes(self,comment,old_status):

            if old_status != self.status:
                if self.status in [settings.STATUS_ACTIVE, settings.STATUS_PAUSED, settings.STATUS_OUT_OF_BALANCE]:
                    for item in self.service_set.all():
                        if item.status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE]:
                            item.set_changestatus_in_plan(self.status)
                if self.status == settings.STATUS_ARCHIVED:
                    for item in self.service_set.all():
                        item.set_changestatus_in_plan(self.status)

                # Создаем запись об изменении статуса абонента        
                asc = AbonentStatusChanges(
                    abonent=self,
                    laststatus=old_status,
                    newstatus=self.status,
                    comment=comment,
                    date=datetime.datetime.now()
                )
                asc.save()

    # Проверка на положительность баланса
    def check_status(self, reason):
        old_status = self.status
        if self.status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE]:
            if self.is_credit == settings.PAY_BEFORE:
                self.status = (settings.STATUS_ACTIVE if self.balance >= 0 else settings.STATUS_OUT_OF_BALANCE)
            else:
                self.status = settings.STATUS_ACTIVE
            super(Abonent, self).save()
            self.set_changes(reason, old_status)

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Abonent.objects.get(pk=self.pk).status
            if old_status != self.status:
                self.set_changes('Изменение статуса', old_status)
            self.check_status('Комплексные причины')
            super(Abonent, self).save(*args, **kwargs)
        else:
            super(Abonent, self).save(*args, **kwargs)
            self.set_changes('Создание нового', '')
   
    class Meta:
        verbose_name = u'Абонент'
        verbose_name_plural = u'Абоненты'       
        
    def __unicode__(self):
        return "%s - %s" % (self.contract, self.title)

class Bank(models.Model):
    title = models.CharField(u'Название', max_length=200)
    bik = models.CharField(u'БИК', max_length=10)
    account = models.CharField(u'кор. счет', max_length=20)

    class Meta:
        verbose_name = u'Банк'
        verbose_name_plural = u'Банки'       
        
    def __unicode__(self):
        return "%s - %s" % (self.bik, self.title)

class Passport(models.Model):
    series = models.CharField(u'Серия', max_length=4, blank=True, null=True)
    number = models.CharField(u'Номер', max_length=6, blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False, verbose_name=u'Дата выдачи', blank=True, null=True)
    issued_by = models.CharField(u'Выдан', max_length=200, blank=True, null=True)
    address = models.CharField(u'Адрес прописки', max_length=200, blank=True, null=True)
    code = models.CharField(u'Код подразделения', max_length=10, blank=True, null=True)
    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент', blank=True, null=True, unique=True)

    class Meta:
        verbose_name = u'Паспорт'
        verbose_name_plural = u'Паспорта'       
        
    def __unicode__(self):
        return "%s %s" % (self.series, self.number)

class Detail(models.Model):
    title = models.CharField(u'Название', max_length=200, blank=True, null=True)
    inn = models.CharField(u'ИНН', max_length=10, blank=True, null=True)
    kpp = models.CharField(u'КПП', max_length=10, blank=True, null=True)
    account = models.CharField(u'рас. счет', max_length=20, blank=True, null=True)
    post_address = models.CharField(u'Почтовый Адрес', max_length=200, blank=True, null=True)
    official_address = models.CharField(u'Юридический адрес', max_length=200, blank=True, null=True)
    bank = models.ForeignKey(Bank, verbose_name=u'Банк', blank=True, null=True)
    abonent = models.ForeignKey(Abonent, verbose_name=u'Абонент', blank=True, null=True, unique=True)

    class Meta:
        verbose_name = u'Реквизиты компании'
        verbose_name_plural = u'Реквизиты компаний'       
        
    def __unicode__(self):
        return "%s - %s" % (self.title, self.inn)

class Service(models.Model):

    macvalidator = RegexValidator('[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$', u'Неправильный формат MAC адреса')    
    abon = models.ForeignKey(Abonent,verbose_name=u'Абонент')
    tos = models.ForeignKey(TypeOfService,verbose_name=u'Тип услуги')
    segment = models.ForeignKey(Segment,verbose_name=u'Сегмент')
    plan = models.ForeignKey(Plan,verbose_name=u'Тарифный план')
    ip = models.OneToOneField(IPAddr, verbose_name=u'IP адрес', blank=True, null= True)
    # vlan = models.OneToOneField(Vlan, verbose_name=u'Vlan', blank=True, null= True,related_name='vlan')
    # vl = models.ForeignKey(Vlan, verbose_name=u'Vlan', blank=True, null= True,related_name='vl')
    vlan = models.ForeignKey(Vlan, verbose_name=u'Vlan', blank=True, null= True,related_name='vlan')
    # vlan_id = models.ForeignKey(Vlan, related_name='vlan_temp', verbose_name=u'Vlan', blank=True, null= True)
    adm_status = models.CharField(u'Административный статус', max_length=1, choices=settings.ADM_STATUSES, default=settings.STATUS_NEW)
    speed_in = models.PositiveIntegerField(default=0, blank=True, null=True)
    speed_out = models.PositiveIntegerField(default=0, blank=True, null=True)
    mac = models.CharField(u'MAC адрес', blank=True, null= True, max_length=17,validators=[macvalidator])
    status = models.CharField(u'Статус', max_length=1, choices=settings.STATUSES, default=settings.STATUS_NEW)
    lat = models.FloatField(u'Latitude', blank=True, null=True)
    lon = models.FloatField(u'Longitude', blank=True, null=True)
    address = models.CharField(u'Адрес', blank=True, null= True, max_length=100)
    # location = models.ForeignKey(Node, verbose_name=u'Местонахождение')
    datestart = models.DateField(auto_now=False, auto_now_add=False, default=datetime.datetime.now(), verbose_name=u'Дата начала')
    datefinish = models.DateField(auto_now=False, auto_now_add=False, blank=True, null= True, verbose_name=u'Дата окончания')
    user_device = models.ForeignKey(Device, related_name='user_device',verbose_name=u'Абонентское устройство', blank=True, null= True)
    bs_device = models.ForeignKey(Device, related_name='bs_device', verbose_name=u'Абонентская БС', blank=True, null= True)

    def set_changestatus_in_plan(self, new_status, date=datetime.datetime.now()):
        ssc = ServiceStatusChanges(
                        service=self,
                        # laststatus=self.status,
                        newstatus=new_status,
                        comment='Изменение статуса услуги',
                        date=date,
                        # done=True,
                        # successfully=True,
                )
        ssc.save()

    def set_status(self, new_status, date=datetime.datetime.now()):
        if self.status == new_status:
            return False

        if self.abon.status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW] and not new_status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW]:
            return False

        else:
            if self.status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE] and new_status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW]:
                self.stop(newstatus=new_status)
            elif self.status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW] and new_status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE]:
                self.start(newstatus=new_status)
            self.status = new_status if not new_status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE] else self.abon.status
            self.save()
            return True

    def stop(self, newstatus=settings.STATUS_ARCHIVED):
        self.status = newstatus
        today = datetime.datetime.today()
        qty_days = calendar.mdays[today.month]
        summ = round(self.plan.price * (qty_days - today.day)/qty_days,2)
        if summ > 0:
            top = pays.models.PaymentSystem.objects.get(pk=4)
            payment = pays.models.Payment(abon=self.abon, top=top, sum=summ, date=datetime.datetime.now())
            payment.save()
        self.save()

    def start(self, newstatus=settings.STATUS_ACTIVE):
        self.status = newstatus
        self.save()
        # Если предоплата, то списываем за услуги сразу. Если нет, платежи будут списаны в начале следующего месяца
        if self.abon.is_credit == 'R':
            today = datetime.datetime.today()
            qty_days = calendar.mdays[today.month]
            summ = round(self.plan.price * (qty_days - today.day + 1)/qty_days,2)
            comment = u'Абонентская плата за %s дней месяца' % (qty_days - today.day + 1)
            wot = pays.models.WriteOffType.objects.get(pk=4)
            write_off = pays.models.WriteOff(abonent=self.abon, service=self, wot=wot,summ=summ, comment=comment, date=datetime.datetime.now())
            write_off.save()

    def save(self, force_insert=False, force_update=False):
        is_new = True if not self.pk else False
        if self.mac:
             self.mac.translate(':,.,-').upper().strip()
        # Проверяем не поменялся ли тарифный план
        if self.pk != None and self.plan.pk != Service.objects.get(pk=self.pk).plan.pk:
            # print Service.objects.get(pk=self.pk).pk
            # print self.plan.pk
            new_service = Service.objects.get(pk=self.pk)
            new_service.pk = None
            new_service.plan = self.plan
            new_service.status = self.status
            new_service.datestart = datetime.date.today() + datetime.timedelta(days=1)
            new_service.save()
            self.datefinish = datetime.date.today()
            self.status = STATUS_ARCHIVED
            if self.datestart and self.datefinish and self.datestart > self.datefinish:
                self.delete()
            else:
                super(Service, self).save(update_fields=['datefinish','status'])
        else:
            super(Service, self).save(force_insert=False, force_update=False)
            # Списываем плату за установку
            if is_new:
                wot = pays.models.WriteOffType.objects.get(title=u'Инсталляция')
                write_off = pays.models.WriteOff(abonent=self.abon, service=self, wot=wot,summ=self.plan.install_price, date=datetime.datetime.now(), comment=u'Подключение услуги [%s]' % (self.plan.title))
                write_off.save()

    class Meta:
        verbose_name = u'Услуга'
        verbose_name_plural = u'Услуги'

    def __unicode__(self):
        return "[%s] : %s - %s" % (self.pk, self.plan.title, self.get_status_display())

class ServiceSuspension(models.Model):
    service = models.ForeignKey(Service, verbose_name=u'Услуга')
    user = models.ForeignKey(User, verbose_name=u'Пользователь', blank=True, null= True)
    datestart = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'Дата начала')
    datefinish = models.DateTimeField(verbose_name=u'Дата завершения', blank=True, null= True)
    comment = models.CharField(u'Комментарии', blank=True, null= True, max_length=200)

    class Meta:
        verbose_name = u'Приостановка услуги'
        verbose_name_plural = u'Приостановка услуг'