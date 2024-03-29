# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Sum
from vlans.models import IPAddr, Vlan, Location 
from journaling.models import AbonentStatusChanges, ServiceStatusChanges
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from datetime import date, datetime, time, timedelta
from calendar import monthrange,month_name
import calendar
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

class Pipe(models.Model):
    speed_in = models.PositiveIntegerField(default=0, blank=True, null=True)
    speed_out = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = u'Pipe'
        verbose_name_plural = u'Pipes'
        ordering = ['speed_in','speed_out']

    def __unicode__(self):
        return u"%s/%s Кбит/с" % (self.speed_in, self.speed_out)

class Plan(models.Model):
    title = models.CharField(max_length=200)
    tos = models.ForeignKey(TypeOfService,verbose_name=u'Группа тарифа')
    segment = models.ManyToManyField(Segment,verbose_name=u'Сегмент')
    speed = models.ForeignKey(Pipe, verbose_name=u'Скорость')
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

    def get_activesrv_count(self):
        return self.service_set.exclude(status=settings.STATUS_ARCHIVED).count()

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
                    date=datetime.now()
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
                    self.status = (settings.STATUS_OUT_OF_BALANCE if (self.balance - settings.TURNOFFBALANCE < -service_sum) or (self.balance < settings.TURNOFFBALANCE and datetime.today().day > 24) else settings.STATUS_ACTIVE)
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
    
    def delete(self, *args, **kwargs):
        self.status = settings.STATUS_ARCHIVED
        self.save()

    class Meta:
        verbose_name = u'Абонент'
        verbose_name_plural = u'Абоненты'     
        ordering = ['-utype','title'] 
        
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
    # macvalidator = RegexValidator('[0-9a-fA-F]{2}([-:])[0-9a-fA-F]{2}(\\1[0-9a-fA-F]{2}){4}$', u'Неправильный формат MAC адреса')
    ip = models.OneToOneField(IPAddr, verbose_name=u'IP адрес', unique=True)
    mac = models.CharField(u'MAC адрес', blank=True, null= True, max_length=17) #,validators=[macvalidator])
    comment = models.CharField(u'Комментарий', max_length=300, blank=True, null= True)
    for_device = models.BooleanField(u'Для оборудования',default=False,editable=False)

    class Meta:
        verbose_name = u'Интерфейс'
        verbose_name_plural = u'Интерфейсы'
        ordering = ['ip']

    def __unicode__(self):
        return u"%s" % (self.ip)

class ServiceEnabledManager(models.Manager):
    def get_queryset(self):
        return super(ServiceEnabledManager, self).get_queryset().filter(status__in=[settings.STATUS_ACTIVE,settings.STATUS_OUT_OF_BALANCE])

class ServiceActiveManager(models.Manager):
    def get_queryset(self):
        return super(ServiceActiveManager, self).get_queryset().filter(status=settings.STATUS_ACTIVE)

def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return date(year,month,day)

# Функция возвращает первый день следующего месяца
def get_1stdaynextmonth(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return date(year,month,1)

def month_year_iter( start_month, start_year, end_month, end_year ):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month
    # ym_end= 12*end_year + end_month - 1
    for ym in range( ym_start, ym_end ):
        y, m = divmod( ym, 12 )
        yield y, m+1

class Service(models.Model):
    abon = models.ForeignKey(Abonent,verbose_name=u'Абонент')
    segment = models.ForeignKey(Segment,verbose_name=u'Сегмент')
    tos = models.ForeignKey(TypeOfService,verbose_name=u'Тип услуги')
    plan = models.ForeignKey(Plan,verbose_name=u'Тарифный план')
    ifaces = models.ManyToManyField(Interface, verbose_name=u'Интерфейсы', blank=True, null= True)
    vlan_list = models.ManyToManyField(Vlan, verbose_name=u'Список Vlan', blank=True, null= True,related_name='vlan_list')
    adm_status = models.CharField(u'Административный статус', max_length=1, choices=settings.ADM_STATUSES, default='0')
    status = models.CharField(u'Статус', max_length=1, choices=settings.STATUSES, default=settings.STATUS_NEW)
    speed = models.ForeignKey(Pipe, blank=True, null=True, verbose_name=u'Скорость')
    location = models.ForeignKey(Location, blank=True, null=True, verbose_name=u'Местонахождение')
    datestart = models.DateField(auto_now=False, auto_now_add=False, default=datetime.now(), verbose_name=u'Дата начала')
    datefinish = models.DateField(auto_now=False, auto_now_add=False, blank=True, null= True, verbose_name=u'Дата окончания')
    device = models.ForeignKey('devices.Device', verbose_name=u'Абонентское устройство', blank=True, null= True)
    objects = models.Manager()
    objects_active = ServiceActiveManager()
    objects_enabled = ServiceEnabledManager()

    def set_changestatus_in_plan(self, new_status, date=datetime.now()):
        ssc = ServiceStatusChanges(
                        service=self,
                        newstatus=new_status,
                        comment='Изменение статуса услуги',
                        date=date)
        ssc.save()

    def recalculate(self,start,end,demo=True):
        # Получаем список изменений тарифов
        chlist = self.serviceplanchanges_set.all().order_by('date')
        # period = {'start':datetime(2014,10,1),'end':datetime(2015,8,31)}
        period = {'start':start,'end':end}
        is_credit = True if self.abon.is_credit == 'O' else False # Проверяем на постоплату
        idx = 0
        
        # Делаем заготовку для пачки спсианий аб. платы
        from pays.models import WriteOff, WriteOffType
        wot = WriteOffType.objects.get(title='Абонентская плата')
        # Удаляем все списание абонплаты по этой услуге за указанный период
        date_range = [period['start'],period['end']] if not is_credit else [add_months(period['start'],1),add_months(period['end'],1)]
        for wo in self.writeoff_set.filter(date__range=date_range,wot=wot):
            wo.delete()

        for spc in chlist:
            datestart = chlist[idx].date
            idx += 1
            datefinish = chlist[idx].date - timedelta(days=1) if len(chlist) >= idx+1 else datetime.today()
            plan = chlist[idx-1].plan

            if period['start'] > datefinish or period['end'] < datestart:
                continue
            datestart = datestart if datestart > period['start'] else period['start']
            datefinish = datefinish if datefinish < period['end'] else period['end']

            for year,month in month_year_iter(datestart.month,datestart.year,datefinish.month,datefinish.year):
                qty_days = monthrange(year,month)[1] # Кол-во дней в месяце
                payday = 1 # День списания аб.платы
                # Это на случай если весь период - один месяц
                if (datefinish.year,datefinish.month) == (year,month):
                    last_day = datefinish.day
                else:
                    last_day = qty_days

                if (datestart.year,datestart.month) == (year,month):
                    # Если это первый месяц
                    payday = datestart.day
                    total_days =  last_day - datestart.day + 1
                elif (datefinish.year,datefinish.month) == (year,month):
                    # Если это последний месяц
                    total_days = datefinish.day
                else:
                    # Подсчет для обычного месяца
                    total_days = qty_days

                comment = 'Абонентская плата за %s, всего дней: %s' % (date(year,month,1).strftime('%B %Y'),total_days)
                date_of_debit = add_months(date(year,month,1),1) if is_credit else date(year,month,payday)
                summ = plan.price * (total_days)/qty_days
                # Делаем новые списания аб.платы
                write_off = WriteOff(abonent=self.abon, service=self, wot=wot,summ=round(summ,2), date=date_of_debit, comment=comment)
                write_off.save()
                print "%s %0.2f руб, %s %s" % (date_of_debit,summ, month,comment)
        # WriteOff.objects.bulk_create(write_off_list)
        # print write_off_list    

    def set_status(self, new_status, date=datetime.now()):
        # Если статус не изменился - выходим
        if self.status == new_status:
            return False

        # Если статус абонента пассивный, а новый статус услуги активный - выходим
        if (self.abon.status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW]) and (new_status not in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW]):
            return False

        # Если статус услуги был активным, а становится пассивным, то останавливаем услугу
        if self.status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE] and new_status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW]:
            self.stop(date, newstatus=new_status)

        # Если статус услуги был пассивным, а стал активным, то стартуем услугу
        elif self.status in [settings.STATUS_ARCHIVED, settings.STATUS_PAUSED, settings.STATUS_NEW] and new_status in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE]:
            self.start(date, newstatus=new_status)

        # Если новый статус услуги пассивный, то присваиваем его, а если активный, то статус услуги = статусу абонента
        self.status = new_status if new_status not in [settings.STATUS_ACTIVE, settings.STATUS_OUT_OF_BALANCE] else self.abon.status
        self.save()
        return True

    def stop(self, date=datetime.now(), newstatus=settings.STATUS_ARCHIVED):
        self.status = newstatus
        today = date.date()
        # qty_days = calendar.mdays[today.month]
        qty_days = monthrange(today.year,today.month)[1]
        summ = self.plan.price * (qty_days - today.day)/qty_days
        if summ > 0 and self.abon.is_credit == settings.PAY_BEFORE:
            from pays.models import PaymentSystem,Payment
            top = PaymentSystem.objects.get(pk=4)
            payment = Payment(abonent=self.abon, top=top, summ=summ, date=date)
            payment.save()
        self.datefinish = date
        self.save()

    def start(self, date=datetime.now(), newstatus=settings.STATUS_ACTIVE):
        self.status = newstatus
        self.datestart = date
        targetday = date.date() # Дата начала услуги
        now = datetime.now() # Текущая дата
        self.save()

        from pays.models import WriteOff, WriteOffType
        wot_install = WriteOffType.objects.get(title=u'Инсталляция')
        wot_abon = WriteOffType.objects.get(title=u'Абонентская плата')

        # qty_days = calendar.mdays[targetday.month] # Считаем число дней в месяце
        qty_days = monthrange(targetday.year,targetday.month)[1]
        summ = self.plan.price * (qty_days - targetday.day + 1)/qty_days # Считаем абоненскую плату за остаток месяца
        comment = u'Абонентская плата за %s дней %s' % (qty_days - targetday.day + 1,targetday.strftime('%B %Y'))

        # Списываем инсталляцию датой активации услуги
        write_off = WriteOff(abonent=self.abon, service=self, wot=wot_install,summ=self.plan.install_price, date=targetday, comment=u'Подключение услуги [%s]' % (self.plan.title))
        write_off.save()
   
        # Если кредитная форма оплаты, но подключен в предыдущем месяце, то списываем абон первым числом следующего месяца.
        if self.abon.is_credit == settings.PAY_CREDIT and (targetday.year*12 + targetday.month) != (now.year*12 + now.month):
            write_off = WriteOff(abonent=self.abon, service=self, wot=wot_abon,summ=summ, comment=comment, date=get_1stdaynextmonth(targetday,1))
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
            write_off = WriteOff(abonent=self.abon, service=self, wot=wot_abon,summ=summa, comment=comment, date=datetime(y,m,1))
            write_off.save()

    def delete(self, *args, **kwargs):
        self.status = settings.STATUS_ARCHIVED
        self.save()

    class Meta:
        verbose_name = u'Услуга'
        verbose_name_plural = u'Услуги'

    def __unicode__(self):
        title = self.abon.title if self.abon.utype == 'U' else self.abon.contract
        return "[%s] %s : %s - %s" % (self.pk, title, self.plan.title, self.get_status_display())

class ServiceSuspension(models.Model):
    service = models.ForeignKey(Service, verbose_name=u'Услуга')
    user = models.ForeignKey(User, verbose_name=u'Пользователь', blank=True, null= True)
    datestart = models.DateTimeField(default=datetime.now, verbose_name=u'Дата начала')
    datefinish = models.DateTimeField(verbose_name=u'Дата завершения', blank=True, null= True)
    comment = models.CharField(u'Комментарии', blank=True, null= True, max_length=200)

    class Meta:
        verbose_name = u'Приостановка услуги'
        verbose_name_plural = u'Приостановка услуг'