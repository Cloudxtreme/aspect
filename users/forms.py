from django import forms
from django.contrib.auth import authenticate
from users.models import Abonent, Service, Plan, TypeOfService, Segment, Agent, Passport, Detail, Interface, Pipe
from vlans.models import Vlan, Location
from devices.models import Device
from users.fields import JSONWidget
from bootstrap3_datetime.widgets import DateTimePicker
# from django.forms.extras.widgets import SelectDateWidget

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

    extratag = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class':'form-control multiple select2-multiple'}),
            label = u'Метки для поиска')

    class Meta:
        model = Abonent
        fields = ['title','notice_email','notice_mobile', 'is_credit', 'status','vip', 'extratag']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Доп.название' }),
            'notice_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}),
            'notice_mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон' }),
            'is_credit': forms.Select(attrs={'class': 'form-control', }),
            'status': forms.Select(attrs={'class': 'form-control', }),
            # 'tag': forms.TextInput(attrs={'class' : 'form-control multiple select2-multiple',}),
            'vip': forms.CheckboxInput(attrs={}),
        }


class PassportForm(forms.ModelForm):
    class Meta:
        model = Passport
        exclude = ['abonent']
        widgets = {
            'series': forms.TextInput(attrs={'class': 'form-control', 'size':'4', }),
            'number': forms.TextInput(attrs={'class': 'form-control', }),
            'date': forms.DateInput(attrs={'class': 'form-control', }),
            'issued_by': forms.TextInput(attrs={'class': 'form-control', }),
            'address': forms.TextInput(attrs={'class': 'form-control', }),
            'code': forms.TextInput(attrs={'class': 'form-control', }),
        }

class DetailForm(forms.ModelForm):
    class Meta:
        model = Detail
        exclude = ['abonent']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'size':'4', }),
            'inn': forms.TextInput(attrs={'class': 'form-control', }),
            'kpp': forms.DateInput(attrs={'class': 'form-control', }),
            'account': forms.TextInput(attrs={'class': 'form-control', }),
            'post_address': forms.TextInput(attrs={'class': 'form-control', }),
            'official_address': forms.TextInput(attrs={'class': 'form-control', }),
            'bank': forms.Select(attrs={'class': 'form-control',}),
        }

class SmartSearchForm(forms.Form):
    string = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete' : 'off', 'placeholder' : 'Поисковый запрос'}), label = u'Поисковый запрос')

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

# Основная форма для редктирования услуги
class GenericServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GenericServiceForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Service

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
    # vlan = forms.ModelChoiceField(queryset=Vlan.objects.order_by('number'),required=False)

    def __init__(self, *args, **kwargs):
        super(ServiceEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Service
        exclude = {'abon', 'status', 'tos', 'datestart','datefinish', 'segment', 'plan','location', 'ifaces'}
        widgets = {
            'vlan_list': forms.SelectMultiple(attrs={'class':'form-control select2-multiple','multiple' : 'multiple',}),
        }

class ServiceInterfaceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceInterfaceForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Interface

class ServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Service
        exclude = {'abon', 'status', 'datestart','datefinish','pipe', 'ip','vlan','adm_status','mac' }


class PipeEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PipeEditForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Pipe

class ServiceLocationForm(forms.ModelForm):
    location = forms.ModelChoiceField(
            queryset=Location.objects.filter(bs_type='CP'),
            widget=forms.Select(attrs={'class':'form-control'}), 
            label = u'Местоположение')

    class Meta:
        model = Service
        fields = ['location']

class ServiceDeviceForm(forms.ModelForm):
    device = forms.ModelChoiceField(
            queryset=Device.objects.all(),
            widget=forms.Select(attrs={'class':'form-control'}), 
            label = u'Устройство')

    change_location = forms.BooleanField(
            required=False,
            widget=forms.CheckboxInput(attrs={'class':'form-control'}),
            label = u'Это персональное конечное устройство')

    class Meta:
        model = Service
        fields = ['device','change_location']

class ServiceSpeedForm(GenericServiceForm):
    class Meta(GenericServiceForm.Meta):
        fields = {'speed',}

class ServiceStateForm(GenericServiceForm):
    class Meta(GenericServiceForm.Meta):
        fields = {'adm_status',}

class ServiceVlanForm(GenericServiceForm):
    class Meta(GenericServiceForm.Meta):
        fields = {'vlan_list',}

class OrgServiceForm(forms.ModelForm):
    # speed = forms.IntegerField(label=u'Скорость доступа, Кбит/с')
    speed = forms.ModelChoiceField(
        queryset =Pipe.objects.all(),
        label=u'Скорость доступа, Кбит/с', 
        widget=forms.Select(attrs={'class' : 'form-control'}),
     )

    datechange = forms.DateField(
        label=u'Дата активации услуги', 
        required=False,
        widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}),
     )

    price = forms.FloatField(label=u'Абон. плата, руб.')
    install_price = forms.FloatField(label=u'Стоимость подключения, руб.')

    def __init__(self, *args, **kwargs):
        super(OrgServiceForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        self.fields['price'].localize = True
        self.fields['install_price'].localize = True
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Service
        fields = {'segment','tos',}

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

class DateFilterForm(forms.Form):
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