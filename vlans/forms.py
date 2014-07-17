from django import forms
from vlans.models import Node
from vlans.widgets import LocationWidget

class LocationForm(forms.ModelForm):
    latlng = forms.CharField(widget=LocationWidget()) # http://djangosnippets.org/snippets/2106/
    class Meta:
        model = Node
#        exclude = ('contact')
