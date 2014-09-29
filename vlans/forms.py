from django import forms
from vlans.models import Location, Vlan
from vlans.widgets import LocationWidget

# class LocationForm(forms.ModelForm):
#     latlng = forms.CharField(widget=LocationWidget()) # http://djangosnippets.org/snippets/2106/
#     class Meta:
#         model = Node
# #        exclude = ('contact')

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