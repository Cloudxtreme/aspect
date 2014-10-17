from django import forms
from devices.models import Device

class DeviceEditForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(DeviceEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Device
        exclude = ['interfaces','last_available']