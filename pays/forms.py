# -*- coding: utf-8 -*- 
from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from pays.models import WriteOff, Payment, PromisedPays, PaymentSystem
from users.models import Abonent
from datetime import datetime
from django.conf import settings

class DateChoiceForm(forms.Form):
    datestart = forms.DateField(label=u'Дата начала', widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False, 'showToday': True }))
    datefinish = forms.DateField(label=u'Дата окончания', widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False, "showToday": True, }))
    utype = forms.MultipleChoiceField(
        choices = settings.U_TYPE,
        label=u'Тип абонента', 
        required=False,
        widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'})
     )
    paymentsystem = forms.MultipleChoiceField(
        choices =PaymentSystem.objects.all().values_list('pk','title'),
        label=u'Платежная система', 
        required=False,
        # initial=False,
        widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'}),
     )

    # def clean(self):
    #     cleaned_data = super(DateChoiceForm, self).clean()
    #     if not self.errors:
    #         if self.datefinish < self.datestart:
    #             raise forms.ValidationError(u'Дата окончания не может быть раньше даты начала')
    #     return cleaned_data

class WriteOffForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
         super(WriteOffForm, self).__init__(*args, **kwargs)
         self.fields['summ'].localize = True
  
    class Meta:
        model = WriteOff
      	exclude = ['abonent', 'user', 'valid']
        fields = ['wot', 'service', 'summ', 'date', 'number', 'comment']  
        
        widgets = {
            'wot': forms.Select(attrs={'class': 'form-control',}),
            'service': forms.Select(attrs={'class': 'form-control',}),
            'summ': forms.TextInput(attrs={'class': 'form-control',}),
            'number': forms.TextInput(attrs={'class': 'form-control',}),
            'comment': forms.Textarea(attrs={'class': 'form-control','rows': 2, 'cols': 40}),
            'date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False, }),
        }


    # def __init__(self, *args, **kwargs):
    #     super(WriteOffForm, self).__init__(*args, **kwargs)
    #     # adding css classes to widgets without define the fields:
    #     for field in self.fields:
    #         self.fields[field].widget.attrs['class'] = 'form-control'

class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
         super(PaymentForm, self).__init__(*args, **kwargs)
         self.fields['summ'].localize = True
    
    class Meta:
        model = Payment
      	fields = ['top', 'summ', 'date','num']  
      	
        widgets = {
            'num': forms.TextInput(attrs={'class': 'form-control',}),
            'top': forms.Select(attrs={'class': 'form-control',}),
            'summ': forms.TextInput(attrs={'class': 'form-control',}),
            'date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False, }),
        }

class QuickPaymentForm(forms.ModelForm):
    abonent = forms.ModelChoiceField(queryset=Abonent.objects.order_by('title'),widget=forms.Select(attrs={'class':'form-control'}), label = u'Абонент')
    
    def __init__(self, *args, **kwargs):
         super(QuickPaymentForm, self).__init__(*args, **kwargs)
         self.fields['sum'].localize = True

    class Meta:
        model = Payment
        fields = ['abonent', 'summ', 'date']
        
        widgets = {
            # 'abonent': forms.TextInput(attrs={'class': 'form-control',}),
            'summ': forms.TextInput(attrs={'class': 'form-control',}),
            'date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False, }),
        }

class PromisedPayForm(forms.ModelForm):
    class Meta:
        model = PromisedPays
        fields = ['summ', 'datestart', 'datefinish','comment']  
        widgets = {
            'summ': forms.TextInput(attrs={'class': 'form-control',}),
            'datestart': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False, }),
            'datefinish': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False, }),
            'comment': forms.Textarea(attrs={'class': 'form-control','rows': 2, 'cols': 40}),
        }