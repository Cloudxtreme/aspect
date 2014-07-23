# -*- coding: utf-8 -*- 
from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
# from django.contrib.auth.models import User
from users.models import Abonent
from django.conf import settings
from datetime import datetime

class AbonentFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AbonentFilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = settings.STATUSES
        self.fields['utype'].choices = settings.U_TYPE
        self.fields['is_credit'].choices = settings.PAYTYPE

    balance_lt = forms.IntegerField(
        label=u'Баланс =<', 
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

class GroupEmailForm(forms.Form):
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
        label=u'Дата', 
        # required=False,
        initial=datetime.now(),
        widget=DateTimePicker(attrs={'class' : 'form-control',})
        )

