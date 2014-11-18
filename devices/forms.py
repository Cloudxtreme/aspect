# -*- coding: utf-8 -*-
from django import forms
from devices.models import Device, Application
from users.models import Interface
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

class DeviceEditForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(DeviceEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Device
        exclude = ['interfaces','last_available','location']

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