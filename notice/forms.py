# -*- coding: utf-8 -*- 
from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
# from django.contrib.auth.models import User
from users.models import Abonent, TypeOfService, Plan
from django.conf import settings
from datetime import datetime
from notice.models import EmailMessage,TemplateMessage,AbonentEvent,SMSMessage

class TemplateMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TemplateMessageForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = TemplateMessage

class SMSMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SMSMessageForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = SMSMessage
        exclude = ['status','sent']

class EmailMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailMessageForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = EmailMessage

class InvoiceMessageForm(EmailMessageForm):
    class Meta(EmailMessageForm.Meta):
        fields = ['abonent','attach',]

class AbonentEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AbonentEventForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = AbonentEvent

class AbonentFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AbonentFilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = settings.STATUSES
        self.fields['utype'].choices = settings.U_TYPE
        self.fields['is_credit'].choices = settings.PAYTYPE

    title = forms.CharField(
        label=u'Название', 
        required=False,
        # initial=0,
        widget=forms.TextInput(attrs={'class' : 'form-control',})
     )

    contract = forms.CharField(
        label=u'Номер договора', 
        required=False,
        # initial=0,
        widget=forms.TextInput(attrs={'class' : 'form-control',})
     )
   
    balance_lt = forms.IntegerField(
        label=u'Баланс <', 
        required=False,
        # initial=0,
        widget=forms.NumberInput(attrs={'class' : 'form-control',})
     )
    balance_gt = forms.IntegerField(
        label=u'Баланс >=', 
        required=False,
        # initial=0,
        widget=forms.NumberInput(attrs={'class' : 'form-control',})
     )
    status = forms.MultipleChoiceField(
        label=u'Статус', 
        required=False,
        # initial=False,
        widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'})
     )

    utype = forms.MultipleChoiceField(
        label=u'Тип абонента', 
        required=False,
        # initial=False,
        widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'})
     )

    is_credit = forms.MultipleChoiceField(
        label=u'Тип оплаты', 
        required=False,
        # initial=False,
        widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'})
     )

    speed_lt = forms.IntegerField(
        label=u'Скорость <', 
        required=False,
        # initial=0,
        widget=forms.NumberInput(attrs={'class' : 'form-control',})
     )

    speed_gt = forms.IntegerField(
        label=u'Скорость >=', 
        required=False,
        # initial=0,
        widget=forms.NumberInput(attrs={'class' : 'form-control',})
     )
    # plan = forms.MultipleChoiceField(
    #     choices =Plan.objects.all().values_list('pk','title'),
    #     label=u'Тарифный план', 
    #     required=False,
    #     # initial=False,
    #     widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'}),
    #  )

    tos = forms.MultipleChoiceField(
        choices =TypeOfService.objects.all().values_list('pk','title'),
        label=u'Тип услуги', 
        required=False,
        # initial=False,
        widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'}),
     )

class GroupEmailForm(forms.Form):
    abonent_list = forms.MultipleChoiceField(
        label=u'Список адресатов', 
        required=False,
        widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'})
     )    
    subject = forms.CharField(
        label=u'Тема', 
        required=True,
        # initial=0,
        widget=forms.TextInput(attrs={'class' : 'form-control',})
     )    
    content = forms.CharField(
        label=u'Сообщение', 
        required=True,
        # initial=0,
        widget=forms.Textarea(attrs={'class' : 'form-control',})
     ) 
    date = forms.DateTimeField(
        label=u'Дата отправки', 
        # required=False,
        initial=datetime.now(),
        widget=DateTimePicker(attrs={'class' : 'form-control',})
        )
