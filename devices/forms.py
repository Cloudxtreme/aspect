# -*- coding: utf-8 -*-
from django import forms
from devices.models import Device, Application
from users.models import Interface, Service
from vlans.models import Location
from bootstrap3_datetime.widgets import DateTimePicker

class AppEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AppEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Application
        exclude = ['author']
        widgets = {
            'date': DateTimePicker(),
            }

class DeviceChoiceLocationForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.filter(bs_type__in=['B','CP']),widget=forms.Select(attrs={'class':'form-control'}), label = u'Местоположение')
    
    class Meta:
        model = Device
        fields = ['location']

class DeviceChoiceServiceForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Service.objects.filter(device=None),widget=forms.Select(attrs={'class':'form-control'}), label = u'Услуга')
    
    class Meta:
        model = Device
        fields = ['service']


class DeviceEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Device
        exclude = ['interfaces','last_available','location']

class IPForm(forms.Form):
    ip = forms.CharField(label=u'IP-адрес', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder' : "10.64.х.х" } ))

class SyslogFilterForm(forms.Form):
    datestart = forms.DateField(
        label=u'Дата начала', 
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False, 'showToday': True }),
        required=False,
        )

    datefinish = forms.DateField(
        label=u'Дата окончания', 
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False, "showToday": True, }),
        required=False,
        )

    host = forms.CharField(
        label=u'IP адрес', 
        required=False,
        widget=forms.TextInput(attrs={'class' : 'form-control',})
     )