from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from pays.models import WriteOff, Payment, PromisedPays

class WriteOffForm(forms.ModelForm):
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
    class Meta:
        model = Payment
      	fields = ['top', 'sum', 'date','num']  
      	
        widgets = {
            'num': forms.TextInput(attrs={'class': 'form-control',}),
            'top': forms.Select(attrs={'class': 'form-control',}),
            'sum': forms.TextInput(attrs={'class': 'form-control',}),
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