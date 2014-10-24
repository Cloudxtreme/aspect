# -*- coding: utf-8 -*-
from django import forms
from devices.models import Device
from users.models import Interface
from bootstrap3_datetime.widgets import DateTimePicker

class DeviceEditForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(DeviceEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Device
        exclude = ['interfaces','last_available']

class SyslogFilterForm(forms.Form):
    datestart = forms.DateField(label=u'Дата начала', widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False, 'showToday': True }))
    datefinish = forms.DateField(label=u'Дата окончания', widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False, "showToday": True, }))
    host = forms.ModelChoiceField(
        queryset = Interface.objects.filter(for_device=True),
        label=u'Адрес', 
        widget=forms.Select(attrs={'class' : 'form-control'}),
     )

    # utype = forms.MultipleChoiceField(
    #     choices = settings.U_TYPE,
    #     label=u'Тип абонента', 
    #     required=False,
    #     widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'})
    #  )

    # paymentsystem = forms.MultipleChoiceField(
    #     choices =PaymentSystem.objects.all().values_list('pk','title'),
    #     label=u'Платежная система', 
    #     required=False,
    #     # initial=False,
    #     widget=forms.SelectMultiple(attrs={'class' : 'form-control select2-multiple','multiple' : 'multiple'}),
    #  )