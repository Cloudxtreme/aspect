from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from journaling.models import ServiceStatusChanges

class ServiceStatusChangesForm(forms.ModelForm):
    class Meta:
        model = ServiceStatusChanges
        fields = ['newstatus', 'date', 'attach', 'comment']
        # fields = ['laststatus','newstatus', 'date', 'datetimefinish', 'attach', 'comment', ]
        widgets = {
            'date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False, }),
            # 'datetimefinish': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       # "pickSeconds": False, }),
            'comment': forms.Textarea(attrs={'class': 'form-control','rows': 2, 'cols': 40}),
            # 'laststatus': forms.Select(attrs={'class': 'form-control',}),
            'newstatus': forms.Select(attrs={'class': 'form-control', }),
            # 'attach': forms.ClearableFileInput(attrs={'class': 'form-control', }),
        }