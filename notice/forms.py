# -*- coding: utf-8 -*- 
from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
# from django.contrib.auth.models import User
# from users.models import Abonent

# class TTForm( forms.ModelForm ):
#     def __init__(self, *args, **kwargs):
#         super(TTForm, self).__init__(*args, **kwargs)
#         users = User.objects.all()
#         self.fields['performer'].choices = [(user.pk, user.get_full_name()) for user in users]

#     class Meta:
#         model = TroubleTicket
#         fields = ['number', 'performer', 'category', 'description']
#         widgets = {
#             'number': forms.TextInput(attrs={'class': 'form-control',}),
#             'performer': forms.Select(attrs={'class': 'form-control', }),
#             'category': forms.Select(attrs={'class': 'form-control', }),
#             'description': forms.Textarea(attrs={'class': 'form-control','rows': 10, 'cols': 20}),
#         }

class MassNoticeForm(forms.Form):
    disabled = forms.BooleanField(
        label=u'Отключены', 
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class':'form-control'})
     )

    less_than_balance = forms.IntegerField(
        label=u'Баланс меньше, чем', 
        required=False,
        widget=forms.NumberInput(attrs={'class':'form-control'})
        )

    subject = forms.CharField(label=u'Тема',widget=forms.TextInput(attrs={'class':'form-control'}))
    message = forms.CharField(label=u'Сообщение',widget=forms.Textarea(attrs={'class':'form-control'}))
    date = forms.DateTimeField(label=u'Дата рассылки',widget=DateTimePicker(attrs={'class':'form-control'}))
