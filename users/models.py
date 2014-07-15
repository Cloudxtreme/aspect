# -*- coding: utf-8 -*-
from django.db import models
from vlans.models import IPAddr, Vlan, Node, Device
# from contacts.models import Contact
from journaling.models import AbonentStatusChanges, ServiceStatusChanges
from django.core.validators import RegexValidator
from users.fields import JSONField
from django.contrib.auth.models import User
import datetime
import calendar
import pays.models
# from pays.models import WriteOffType, WriteOff

# Create your models here.

STATUS_ACTIVE = 'A'
STATUS_OUT_OF_BALANCE = 'N'
STATUS_PAUSED = 'S'
STATUS_ARCHIVED = 'D'
STATUS_NEW = 'W'
PAY_CREDIT = 'O'
PAY_BEFORE = 'R'

STATUSES = (
    (STATUS_NEW, 'Новый'),
    (STATUS_ACTIVE, 'Активный'),
    (STATUS_PAUSED, 'Приостановлен'),
    (STATUS_OUT_OF_BALANCE, 'Отключен за неуплату'),
    (STATUS_ARCHIVED, 'Архив'),
)

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
        return u"%s - %s руб/мес" % (self.title, self.price)

# class Contact(models.Model):
#     surname = models.CharField(u'Фамилия', max_length=50,blank=True, null=True)
#     first_name = models.CharField(u'Имя', max_length=50,blank=True, null=True)
#     second_name = models.CharField(u'Отчество', max_length=50,blank=True, null=True)
#     position = models.CharField(u'Должность', max_length=30,blank=True, null=True)
#     phone = models.CharField(u'Телефон', max_length=12,blank=True, null=True)
#     mobile = models.CharField(u'Мобильный',max_length=12,blank=True, null=True)
#     fax = models.CharField(u'Факс',max_length=12,blank=True, null=True)
#     email = models.CharField(max_length=50,blank=True, null=True)
#     address = models.CharField(u'Адрес',max_length=200,blank=True, null=True)

#     class Meta:
#         verbose_name = u'Контакт'
#         verbose_name_plural = u'Контакты'

#     def _get_full_name(self):
#         "Returns the person's full name."
#         return '%s %s %s' % (self.first_name, self.second_name, self.surname)
#     full_name = property(_get_full_name) 

#     def __unicode__(self):
#         return self.full_name

# class Reason(models.Model):       
#     comment = models.CharField(u'Комментарий', max_length=30)
#     file = models.FileField(upload_to='user_files',blank=True, null=True)

# # pk = 1 'Изменение баланса'
# # pk = 2 'Изменение статуса'
# # pk = 3 'Создание нового'

#     class Meta:
#         verbose_name = u'Основание'
#         verbose_name_plural = u'Основания' 
    
# #    def save(self, force_insert=False, force_update=False):
# #        if self.pk > 3:
# #            super(Reason, self).save(force_insert, force_update)
    
#     def __unicode__(self):
#         return self.comment

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


class Abonent(models.Model):
    U_TYPE = (
        ('F', 'Физическое лицо'),
        ('U', 'Юридическое лицо'),
    )
    PAYTYPE =(
        ('R', 'Предоплата'),
        ('O', 'В кредит')
    )
    title = models.CharField(u'Название', max_length=70)
    contract = models.CharField(u'Номер договора',max_length=15,blank=True, null=True)
    # contact = models.ManyToManyField('contacts.Contact', blank=True)
    status = models.CharField(u'Статус',max_length=1, choices=STATUSES, default=STATUS_NEW)
    utype = models.CharField(u'Тип абонента', max_length=1, choices=U_TYPE)
    is_credit = models.CharField(u'Тип оплаты', max_length=1, choices=PAYTYPE)
    agent = models.ForeignKey(Agent,verbose_name=u'Агент',blank=True, null=True, )
    balance = models.FloatField(u'Баланс', default = 0)
    reserve = models.FloatField(u'Резерв', default = 0)
    rest = models.FloatField(u'Остаток', default = 0)
    notice_email = models.CharField(u'Email для уведомлений', max_length=70, blank=True, null=True)
    notice_mobile = models.CharField(u'Телефон для уведомлений', max_length=13, blank=True, null=True)
    # passport = models.ForeignKey(Passport, verbose_name=u'Паспортные данные', blank=True, null=True)
    # detail = models.ForeignKey(Detail, verbose_name=u'Реквизиты', blank=True, null=True)


    # def switch_services(self):
    #     if not self.is_credit:
    #         try:
    #             for item in Service.objects.get(abon=self.pk):
    #                 if item.status == STATUS_ACTIVE or item.status == STATUS_OUT_OF_BALANCE:
    #                     item.status = self.status
    #         except Service.DoesNotExist:
    #             return None
    
    # Перенос статуса абонента на услуги
    def set_changes(self,comment,old_status):
            # if self.status in [STATUS_ACTIVE, STATUS_PAUSED, STATUS_OUT_OF_BALANCE]:
            #     for item in self.service_set.all():
            #         if item.status in [STATUS_ACTIVE, STATUS_OUT_OF_BALANCE]:
            #             # item.set_changestatus_in_plan(self.status)
            #             # item.status = self.status
            #             # item.save()
            # if self.status == STATUS_ARCHIVED:
            #     for item in self.service_set.all():
            #         # item.set_changestatus_in_plan(self.status)
            #         # item.status = self.status
            #         # item.save()

            if old_status != self.status:
                if self.status in [STATUS_ACTIVE, STATUS_PAUSED, STATUS_OUT_OF_BALANCE]:
                    for item in self.service_set.all():
                        if item.status in [STATUS_ACTIVE, STATUS_OUT_OF_BALANCE]:
                            item.set_changestatus_in_plan(self.status)
                if self.status == STATUS_ARCHIVED:
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
        if self.status in [STATUS_ACTIVE, STATUS_OUT_OF_BALANCE]:
            if self.is_credit == PAY_BEFORE:
                self.status = (STATUS_ACTIVE if self.balance >= 0 else STATUS_OUT_OF_BALANCE)
            else:
                self.status = STATUS_ACTIVE
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

    # def save(self, *args, **kwargs):
    #     old_status = Abonent.objects.get(pk=self.pk).status
    #     super(Abonent, self).save(*args, **kwargs)
    #     comment = 'Изменение статуса'
    #     if self.status in ['A','N']:
    #         d = {True : 'A', False : 'N'}
    #         self.status = d[self.balance >= 0]
    #         comment = 'Изменение баланса'
            
    #     if self.pk:
    #         if self.status != old_status: #Abonent.objects.get(pk=self.pk).status:
    #             asc = AbonentStatusChanges(abonent=self, laststatus = Abonent.objects.get(pk=self.pk).status, newstatus=self.status, comment = comment, datetime = datetime.datetime.now())
    #             asc.save()                
    #     else:
    #         super(Abonent, self).save(*args, **kwargs)
    #         asc = AbonentStatusChanges(abonent=self, newstatus=self.status, comment = 'Создание нового', datetime = datetime.datetime.now())
    #         asc.save()
            
    #     #super(Abonent, self).save(*args, **kwargs)    
   
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
    ADM_STATUSES = (
        ('0', 'По состоянию'),
        ('1', 'Включен вручную'),
        ('2', 'Выключен вручную'),
    )
    macvalidator = RegexValidator('[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$', u'Неправильный формат MAC адреса')    
    abon = models.ForeignKey(Abonent,verbose_name=u'Абонент')
    tos = models.ForeignKey(TypeOfService,verbose_name=u'Тип услуги')
    segment = models.ForeignKey(Segment,verbose_name=u'Сегмент')
    plan = models.ForeignKey(Plan,verbose_name=u'Тарифный план')
    ip = models.OneToOneField(IPAddr, verbose_name=u'IP адрес', blank=True, null= True)
    adm_status = models.CharField(u'Административный статус', max_length=1, choices=ADM_STATUSES, default=STATUS_NEW)
    speed_in = models.PositiveIntegerField(default=0, blank=True, null=True)
    speed_out = models.PositiveIntegerField(default=0, blank=True, null=True)
    mac = models.CharField(u'MAC адрес', blank=True, null= True, max_length=17,validators=[macvalidator])
    status = models.CharField(u'Статус', max_length=1, choices=STATUSES, default=STATUS_NEW)
    lat = models.FloatField(u'Latitude', blank=True, null=True)
    lon = models.FloatField(u'Longitude', blank=True, null=True)
    address = models.CharField(u'Адрес', blank=True, null= True, max_length=100)
    # location = models.ForeignKey(Node, verbose_name=u'Местонахождение')
    datestart = models.DateField(auto_now=False, auto_now_add=False, default=datetime.datetime.now(), verbose_name=u'Дата начала')
    datefinish = models.DateField(auto_now=False, auto_now_add=False,blank=True, null= True, verbose_name=u'Дата окончания')
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

        if self.abon.status in [STATUS_ARCHIVED, STATUS_PAUSED, STATUS_NEW] and not new_status in [STATUS_ARCHIVED, STATUS_PAUSED, STATUS_NEW]:
            return False

        else:
            if self.status in [STATUS_ACTIVE, STATUS_OUT_OF_BALANCE] and new_status in [STATUS_ARCHIVED, STATUS_PAUSED, STATUS_NEW]:
                self.stop(newstatus=new_status)
            elif self.status in [STATUS_ARCHIVED, STATUS_PAUSED, STATUS_NEW] and new_status in [STATUS_ACTIVE, STATUS_OUT_OF_BALANCE]:
                self.start(newstatus=new_status)
            self.status = new_status if not new_status in [STATUS_ACTIVE, STATUS_OUT_OF_BALANCE] else self.abon.status
            self.save()
            return True

    def stop(self, newstatus=STATUS_ARCHIVED):
        self.status = newstatus
        today = datetime.datetime.today()
        qty_days = calendar.mdays[today.month]
        summ = round(self.plan.price * (qty_days - today.day)/qty_days,2)
        if summ > 0:
            top = pays.models.PaymentSystem.objects.get(pk=4)
            payment = pays.models.Payment(abon=self.abon, top=top, sum=summ, date=datetime.datetime.now())
            payment.save()
        self.save()

    def start(self, newstatus=STATUS_ACTIVE):
        self.status = newstatus
        today = datetime.datetime.today()
        qty_days = calendar.mdays[today.month]
        summ = round(self.plan.price * (qty_days - today.day + 1)/qty_days,2)
        comment = u'Абонентская плата за %s дней месяца' % (qty_days - today.day + 1)
        wot = pays.models.WriteOffType.objects.get(pk=4)
        write_off = pays.models.WriteOff(abonent=self.abon, service=self, wot=wot,summ=summ, comment=comment, date=datetime.datetime.now())
        self.save()
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