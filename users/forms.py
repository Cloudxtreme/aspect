from django import forms
from django.contrib.auth import authenticate
from users.models import Abonent, Service, Plan, TypeOfService, Segment, Agent, Passport, Detail
from vlans.models import Vlan
from users.fields import JSONWidget
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms.extras.widgets import SelectDateWidget

# class ContactForm(forms.ModelForm):
#     class Meta:
#         model = Contact
# #        exclude = ('contact')JSONWidget

class AbonentForm(forms.ModelForm):
    class Meta:
        model = Abonent
        fields = ['title', 'contract', 'is_credit', 'utype']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО или название'}),
            'contract': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Номер договора' }),
            'is_credit': forms.Select(attrs={'class': 'form-control', }),
            'utype': forms.Select(attrs={'class': 'form-control', }),
        }

class ManageForm(forms.ModelForm):
    class Meta:
        model = Abonent
        fields = ['title','notice_email','notice_mobile', 'is_credit', 'status','vip']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled', 'placeholder': 'Доп.название' }),
            'notice_email': forms.EmailInput(attrs={'class': 'form-control', 'disabled':'disabled', 'placeholder': 'E-Mail'}),
            'notice_mobile': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled', 'placeholder': 'Телефон' }),
            'is_credit': forms.Select(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'status': forms.Select(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'vip': forms.CheckboxInput(attrs={'disabled':'disabled'}),
        }


class PassportForm(forms.ModelForm):
    class Meta:
        model = Passport
        exclude = ['abonent']
        widgets = {
            'series': forms.TextInput(attrs={'class': 'form-control', 'size':'4', 'disabled':'disabled'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
        }

class DetailForm(forms.ModelForm):
    class Meta:
        model = Detail
        exclude = ['abonent']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'size':'4', 'disabled':'disabled'}),
            'inn': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'kpp': forms.DateInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'account': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'post_address': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'official_address': forms.TextInput(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'bank': forms.Select(attrs={'class': 'form-control','disabled':'disabled'}),
        }

class SearchForm(forms.ModelForm):
    tos = forms.ModelChoiceField(queryset=TypeOfService.objects.all(), widget=forms.Select(attrs={'class':'form-control'}), label = u'Тип услуги' )
    plan = forms.ModelChoiceField(queryset=Plan.objects.all(), widget=forms.Select(attrs={'class':'form-control'}), label = u'Тарифный план')
    segment = forms.ModelChoiceField(queryset=Segment.objects.all(), widget=forms.Select(attrs={'class':'form-control'}), label = u'Сегмент')
    agent = forms.ModelChoiceField(queryset=Agent.objects.all(), widget=forms.Select(attrs={'class':'form-control'}), label = u'Агент')
    IPAddr = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label = u'IP адрес')
    MACaddr = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label=u'МАС адрес')
    
    class Meta:
        model = Abonent
        exclude = ['contact', 'reserve', 'rest']
        widgets = {
            'utype': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_credit': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'contract': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ServicePlanForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset =Plan.objects.all().values_list('pk','title'),
        label=u'Тарифный план', 
        widget=forms.Select(attrs={'class' : 'form-control'}),
     )

    datechange = forms.DateField(
        label=u'Даты смены тарифа', 
        widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}),
     )

class ServiceEditForm(forms.ModelForm):
    vlan = forms.ModelChoiceField(queryset=Vlan.objects.order_by('number'),required=False)

    def __init__(self, *args, **kwargs):
        super(ServiceEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Service
        exclude = {'abon', 'status', 'tos', 'datestart','datefinish', 'segment', 'plan' }


class ServiceForm(forms.ModelForm):
    vlan = forms.ModelChoiceField(queryset=Vlan.objects.order_by('number'),required=False)

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Service
        exclude = {'abon', 'status', }

        widgets = {
            # 'segment': forms.Select(attrs={'class': 'form-control'}),
            'datestart': DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}),
            'datefinish': DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False }),
            'mac': forms.TextInput(attrs={'class': 'form-control', 'placeholder' : '00:12:34:56:78:90'}),
            'speed_in': forms.TextInput(attrs={'class': 'form-control',  'placeholder' : 'Kbps', 'disabled' : 'disabled'}),
            'speed_out': forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Kbps', 'disabled' : 'disabled'}),
            'lat': forms.TextInput(attrs={'class': 'form-control', 'placeholder' : '60.00000'}),
            'lon': forms.TextInput(attrs={'class': 'form-control', 'placeholder' : '30.00000'}),
            # 'status': forms.Select(attrs={'class': 'form-control',}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(label=u'Имя пользователя', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder' : "Имя пользователя" } ))
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder' : "Пароль"} ))

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        if not self.errors:
            user = authenticate(username=cleaned_data['username'], password=cleaned_data['password'])
            if user is None:
                raise forms.ValidationError(u'Имя пользователя и пароль не подходят')
            self.user = user
        return cleaned_data

    def get_user(self):
        return self.user or None