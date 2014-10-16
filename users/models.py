# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Sum
from vlans.models import IPAddr, Vlan, Node, Location 
from devices.models import Device
# from contacts.models import Contact
from journaling.models import AbonentStatusChanges, ServiceStatusChanges
from django.core.validators import RegexValidator
from users.fields import JSONField
from django.contrib.auth.models import User
import datetime
import calendar
# import pays.models
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
    visible = models.BooleanField(u'Видимость',default=True)

    class Meta:
        verbose_name = u'Тип услуги'
        verbose_name_plural = u'Типы услуг'

    def __unicode__(self):
        return self.title

class Tag(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return u"%s" % (self.title)

class Plan(models.Model):
    title = models.CharField(max_length=200)
    tos = models.ForeignKey(TypeOfService,verbose_name=u'Группа тарифа')
    segment = models.ManyToManyField(Segment,verbose_name=u'Сегмент')
    speed_in = models.PositiveIntegerField(blank=True, null=True)
    speed_out = models.PositiveIntegerField(blank=True, null=True)
    comment = models.CharField(max_length=200,blank=True, null=True)
    utype = models.CharField(u'Тип абонента', max_length=1, choices=settings.U_TYPE)
    price = models.FloatField(u'Абон. плата')
    install_price = models.FloatField(u'Стоимость подключения',default=0)
    visible = models.BooleanField(u'Видимость',default=True)

    class Meta:
        verbose_name = u'Тарифный план'
        verbose_name_plural = u'Тарифные планы'

    def __unicode__(self):
        return u"[%s] %s %s - %s руб/мес" % (self.pk, self.tos, self.title, self.price)

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
    def filter_list(self,title='',contract='',status=[],utype=[],tos=[],is_credit=[],balance_lt=None,balance_gt=None,speed_lt=None,speed_gt=None):
        abonent_list = super(AbonentFilterManager, self).get_query_set()
        if title:
            abonent_list = abonent_list.filter(title__icontains=title)|abonent_list.filter(detail__title__icontains=title)
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
        if speed_lt or speed_lt==0:
            pass
            # abonent_list = abonent_list.filter(balance__lt=balance_lt)
        if speed_gt or speed_gt==0:
            pass
            # abonent_list = abonent_list.filter(balance__gte=balance_gt)
        return abonent_list

    def get_query_set(self):
        return super(AbonentFilterManager, self).get_query_set()

class Abonent(models.Model):
    title = models.CharField(u'Доп. название', max_length=200)
    contract = models.CharField(u'Номер договора',max_length=15,blank=True, null=True)
    status = models.CharField(u'Статус',max_length=1, choices=settings.STATUSES, default=settings.STATUS_NEW)
    utype = models.CharField(u'Тип абонента', max_length=1, choices=settings.U_TYPE)
    is_credit = models.CharField(u'Тип оплаты', max_length=1, choices=settings.PAYTYPE)
    agent = models.ForeignKey(Agent,verbose_name=u'Агент', blank=True, null=True)
    balance = models.FloatField(u'Баланс', default = 0)
    reserve = models.FloatField(u'Резерв', default = 0)
    rest = models.FloatField(u'Остаток', default = 0)
    vip = models.BooleanField(u'VIP Клиент', default=False)
    notice_email = models.CharField(u'Email для уведомлений', max_length=70, blank=True, null=True)
    notice_mobile = models.CharField(u'Телефон для уведомлений', max_length=13, blank=True, null=True)
    tag = models.ManyToManyField(Tag,verbose_name=u'Тэг', blank=True, null=True)
    objects = models.Manager()
    obj = AbonentFilterManager()

    def set_changes(self,comment,old_status):
            # Процедура смены статусов всех услуг абонента
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

    # Установка статуса в зависимости от баланса
    def check_status(self, reason):
        old_status = self.status
        if self.vip:
            self.status = settings.STATUS_ACTIVE
            super(Abonent, self).save()
            self.set_changes(reason, old_status)
        else:
            if self.status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE]:
                if self.is_credit == settings.PAY_BEFORE: # Предоплатников выключаем по балансу всегда
                    self.status = (settings.STATUS_ACTIVE if self.balance >= settings.TURNOFFBALANCE else settings.STATUS_OUT_OF_BALANCE)
                else: # Постоплатников c минусовым балансом выключаем 25 числа или в любой другой день, как только сумма на счете станет меньше чем сумма всех услуг
                    service_sum = self.service_set.filter(status__in=['A','N']).aggregate(Sum('plan__price'))['plan__price__sum'] or 0
                    self.status = (settings.STATUS_OUT_OF_BALANCE if (self.balance - settings.TURNOFFBALANCE < -service_sum  ) or (self.balance < settings.TURNOFFBALANCE and datetime.datetime.today().day > 24) else settings.STATUS_ACTIVE)
                super(Abonent, self).save()
                self.set_changes(reason, old_status)

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Abonent.objects.get(pk=self.pk).status
            last_vip_state = Abonent.objects.get(pk=self.pk).vip
            if old_status != self.status:
                self.set_changes('Изменение статуса', old_status)
            if last_vip_state != self.vip:
                self.check_status('Изменен VIP статус')
            else:
                self.check_status('Комплексные причины')
            super(Abonent, self).save(*args, **kwargs)
        else:
            super(Abonent, self).save(*args, **kwargs)
            self.set_changes('Создание нового', '')
   
    class Meta:
        verbose_name = u'Абонент'
        verbose_name_plural = u'Абоненты'       
        
    def __unicode__(self):
        if self.utype == settings.U_TYPE_UR:
            company_name = Detail.objects.get(abonent=self).title
            return "%s - %s (%s)" % (self.contract, company_name, self.title)
        else:
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

class Interface(models.Model):
    macvalidator = RegexValidator('[0-9a-fA-F]{2}([-:])[0-9a-fA-F]{2}(\\1[0-9a-fA-F]{2}){4}$', u'Неправильный формат MAC адреса')
    ip = models.OneToOneField(IPAddr, verbose_name=u'IP адрес', unique=True)
    mac = models.CharField(u'MAC адрес', blank=True, null= True, max_length=17,validators=[macvalidator])
    comment = models.CharField(u'Комментарий', max_length=300, blank=True, null= True)

    class Meta:
        verbose_name = u'Интерфейс'
        verbose_name_plural = u'Интерфейсы'
        ordering = ['ip']

    def __unicode__(self):
        return "%s - %s" % (self.ip, self.mac)

class Service(models.Model):
    abon = models.ForeignKey(Abonent,verbose_name=u'Абонент')
    segment = models.ForeignKey(Segment,verbose_name=u'Сегмент')
    tos = models.ForeignKey(TypeOfService,verbose_name=u'Тип услуги')
    plan = models.ForeignKey(Plan,verbose_name=u'Тарифный план')
    ifaces = models.ManyToManyField(Interface, verbose_name=u'Интерфейсы', blank=True, null= True)
    # Deprecated field
    ip = models.OneToOneField(IPAddr, verbose_name=u'IP адрес', blank=True, null= True)
    vlan_list = models.ManyToManyField(Vlan, verbose_name=u'Список Vlan', blank=True, null= True,related_name='vlan_list')
    adm_status = models.CharField(u'Административный статус', max_length=1, choices=settings.ADM_STATUSES, default='0')
    speed_in = models.PositiveIntegerField(default=0, blank=True, null=True)
    speed_out = models.PositiveIntegerField(default=0, blank=True, null=True)
    status = models.CharField(u'Статус', max_length=1, choices=settings.STATUSES, default=settings.STATUS_NEW)
    location = models.ForeignKey(Location, blank=True, null=True, verbose_name=u'Местонахождение')
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
                self.stop(date, newstatus=new_status)
            elif self.status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW] and new_status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE]:
                self.start(date, newstatus=new_status)
            self.status = new_status if not new_status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE] else self.abon.status
            self.save()
            return True

    def stop(self, date=datetime.datetime.now(), newstatus=settings.STATUS_ARCHIVED):
        self.status = newstatus
        # today = datetime.datetime.today()
        today = date.date()
        qty_days = calendar.mdays[today.month]
        summ = self.plan.price * (qty_days - today.day)/qty_days
        if summ > 0:
            from pays.models import PaymentSystem,Payment
            top = PaymentSystem.objects.get(pk=4)
            payment = Payment(abon=self.abon, top=top, sum=summ, date=date)
            payment.save()
        self.datefinish = date
        self.save()

    def start(self, date=datetime.datetime.now(), newstatus=settings.STATUS_ACTIVE):
        self.status = newstatus
        self.datestart = date
        targetday = date.date() # Дата начала услуги
        now = datetime.datetime.now() # Текущая дата
        self.save()

        from pays.models import WriteOff, WriteOffType
        wot_install = WriteOffType.objects.get(title=u'Инсталляция')
        wot_abon = WriteOffType.objects.get(title=u'Абонентская плата')

        qty_days = calendar.mdays[targetday.month] # Считаем число дней в месяце
        summ = self.plan.price * (qty_days - targetday.day + 1)/qty_days # Считаем абоненскую плату за остаток месяца
        comment = u'Абонентская плата за %s дней %s' % (qty_days - targetday.day + 1,targetday.strftime('%B %Y'))

        # Списываем инсталляцию датой активации услуги
        write_off = WriteOff(abonent=self.abon, service=self, wot=wot_install,summ=self.plan.install_price, date=targetday, comment=u'Подключение услуги [%s]' % (self.plan.title))
        write_off.save()
   
        # Если кредитная форма оплаты, но подключен в предыдущем месяце, то списываем абон первым числом.
        if self.abon.is_credit == settings.PAY_CREDIT and (targetday.year*12 + targetday.month) != (now.year*12 + now.month):
            write_off = WriteOff(abonent=self.abon, service=self, wot=wot_abon,summ=summ, comment=comment, date=datetime.datetime(targetday.year,targetday.month+1,1))
            write_off.save()

        # Если предоплата, то списываем за услуги сразу. Если нет, платежи будут списаны в начале следующего месяца
        if self.abon.is_credit == settings.PAY_BEFORE:
            write_off = WriteOff(abonent=self.abon, service=self, wot=wot_abon,summ=summ, comment=comment, date=targetday)
            write_off.save()

        # Списываем абонентскую плату за прошедшие месяцы
        post_month_shift = 0 if self.abon.is_credit == settings.PAY_BEFORE else 1 # Сдвиг месяцев для постоплатчиков
        
        for month in range((targetday.year*12)+targetday.month+1+post_month_shift,(now.year*12)+now.month+1):
            summa = self.plan.price
            # Дурацкая проблема с декабрем, решаем пока вручную
            if month%12 == 0:
                y = month/12 - 1
                m = 12
            else:
                y = month/12
                m = month%12

            comment = u'Абонентская плата за %s %s г.' % (calendar.month_name[m - post_month_shift],y)
            write_off = WriteOff(abonent=self.abon, service=self, wot=wot_abon,summ=summa, comment=comment, date=datetime.datetime(y,m,1))
            write_off.save()

    class Meta:
        verbose_name = u'Услуга'
        verbose_name_plural = u'Услуги'

    def __unicode__(self):
        return "[%s] %s : %s - %s" % (self.pk, self.abon.title, self.plan.title, self.get_status_display())

class ServiceSuspension(models.Model):
    service = models.ForeignKey(Service, verbose_name=u'Услуга')
    user = models.ForeignKey(User, verbose_name=u'Пользователь', blank=True, null= True)
    datestart = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'Дата начала')
    datefinish = models.DateTimeField(verbose_name=u'Дата завершения', blank=True, null= True)
    comment = models.CharField(u'Комментарии', blank=True, null= True, max_length=200)

    class Meta:
        verbose_name = u'Приостановка услуги'
        verbose_name_plural = u'Приостановка услуг'