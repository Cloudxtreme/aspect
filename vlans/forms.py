from django import forms
from vlans.models import Location, Vlan, Network
from vlans.widgets import LocationWidget

class NetworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NetworkForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    class Meta:
        model = Network
        exclude = ['parent','segment','decip']

class LocationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Location

class VlanEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VlanEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Vlan