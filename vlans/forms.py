from django import forms
from vlans.models import Location, Vlan, Network
from vlans.widgets import LocationWidget

# class LocationForm(forms.ModelForm):
#     latlng = forms.CharField(widget=LocationWidget()) # http://djangosnippets.org/snippets/2106/
#     class Meta:
#         model = Node
# #        exclude = ('contact')

class NetworkForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(NetworkForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Network
        exclude = ['parent','segment','decip']
        # widgets = {
            # 'mask': forms.TextInput(attrs={'class': 'form-control', 'size':'4', }),
            # 'ip': forms.TextInput(attrs={'class': 'form-control', }),
        #     'kpp': forms.DateInput(attrs={'class': 'form-control', }),
        #     'account': forms.TextInput(attrs={'class': 'form-control', }),
        #     'post_address': forms.TextInput(attrs={'class': 'form-control', }),
        #     'official_address': forms.TextInput(attrs={'class': 'form-control', }),
        #     'bank': forms.Select(attrs={'class': 'form-control',}),
        # }

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