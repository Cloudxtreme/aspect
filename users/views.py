# -*- coding: utf-8 -*- 
# from django.shortcuts import render
from django.shortcuts import render_to_response, render, HttpResponseRedirect
from requests.auth import HTTPDigestAuth
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core import serializers
from django.template import RequestContext
from users.forms import  ServiceForm, OrgServiceForm, SearchForm, LoginForm, \
                         PassportForm, DetailForm, ManageForm, AbonentForm, \
                         ServicePlanForm, ServiceEditForm, ServiceInterfaceForm, \
                         ServiceSpeedForm, ServiceStateForm, ServiceVlanForm, \
                         SmartSearchForm, ServiceLocationForm, \
                         ServiceDeviceForm
from journaling.forms import ServiceStatusChangesForm
from notice.forms import AbonentFilterForm
from users.models import Abonent, Service, TypeOfService, Plan, Passport, Detail, Interface, Segment,Tag
from tt.models import TroubleTicket, TroubleTicketComment
from journaling.models import ServiceStatusChanges, AbonentStatusChanges, ServicePlanChanges
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from vlans.models import Network, IPAddr, Vlan
from vlans.forms import LocationForm
from django.db.models import Avg, Max, Min, Sum, Q
from django.conf import settings
from pays.models import Payment
from notes.models import Note
from vlans.models import Location
from contacts.models import Contact
from devices.aux import dec2ip,ip2dec
from devices.models import Device
from users.aux import abonent_filter
import MySQLdb, requests, re
from datetime import datetime, time, timedelta, date
from users.aux import *


def zapret(request):
    return render_to_response('zapret.html')

def balance(request):
    ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
    try:
        balance = '%s руб.' % round(Abonent.objects.get(service__ifaces__ip__ip=ip).balance,2)
    except:
        balance = 'неизвестен'
    return render_to_response('balance.html', { 'balance': balance })


@login_required 
def aquicksearch(request):
    data = request.GET['q']
    abonent_list = abonent_filter(data)
    paginator = Paginator(abonent_list, 10)

    page = request.GET.get('page')
    try:
        abonents = paginator.page(page)
    except PageNotAnInteger:
        abonents = paginator.page(1)
    except EmptyPage:
        abonents = paginator.page(paginator.num_pages)

    if abonent_list.count() == 1:
        return HttpResponseRedirect(reverse('abonent_info', 
            args=[abonent_list.first().pk]))
    elif abonent_list.count() == 0:
        return render_to_response('deadend.html', 
            { 'message' : u'Абоненты не найдены', 
               'previous_page' : request.META['HTTP_REFERER'] 
            }  , context_instance = RequestContext(request))
    else:
        return render_to_response('aqsearch_result.html', 
            { 'abonents' : abonents, 
              'abonent_list_count' : len(abonent_list), 
              'previous_request' : data } , 
              context_instance = RequestContext(request))            

@login_required
def feeds_plans_by_tos(request):
    if request.is_ajax():
        # print request.GET['id'], request.GET['seg']
        if request.GET['id'] == '0' or request.GET['seg'] == '0':
            json_subcat = serializers.serialize("json", Plan.objects.none())
        else:
            json_subcat = serializers.serialize("json", Plan.objects.filter(utype=request.GET['utype'],tos__pk=request.GET['id'],segment__pk=request.GET['seg']))
        return HttpResponse(json_subcat, mimetype="application/javascript")
    else:
        form = ServiceForm() # An unbound form
        return render_to_response('asearch.html', {'form': form})

@login_required
def feeds_ip_by_seg(request):
    if request.GET['id'] == '0':
        json_subcat = serializers.serialize("json", IPAddr.objects.none())
    else:
        data = IPAddr.objects.filter(net__segment__pk=request.GET['id']).filter(net__net_type='UN').filter(Q(interface=None))|IPAddr.objects.filter(service__pk=request.GET['id'])
        json_subcat = serializers.serialize("json", data)
    return HttpResponse(json_subcat, mimetype="application/javascript")


@login_required
def unfilled_params(request,param):
    def zero():
        return []

    def dev_wo_location():
        result = []
        for device in Device.objects.filter(location=None):
            result.append({'url':reverse('device_view', args=[device.pk]),'title': device.__unicode__() })
        return result

    def srv_wo_location():
        result = []
        for service in Service.objects_enabled.filter(location__geolocation=None):
            result.append({'url':reverse('abonent_services', args=[service.abon.pk]),'title': service.__unicode__() }) 
        return result

    def srv_wo_iface():
        result = []
        for service in Service.objects_enabled.filter(tos__pk=1,ifaces=None):
            result.append({'url':reverse('abonent_services', args=[service.abon.pk]),'title': service.__unicode__() }) 
        return result    

    def srv_wo_device():
        result = []
        for service in Service.objects_enabled.filter(device=None,tos__id__in=[1,4]):
            result.append({'url':reverse('abonent_services', args=[service.abon.pk]),'title': service.__unicode__() }) 
        return result   

    def arch_srv_w_device():
        result = []
        for service in Service.objects.filter(status=settings.STATUS_ARCHIVED,device__isnull=False):
            result.append({'url':reverse('abonent_services', args=[service.abon.pk]),'title': service.__unicode__() }) 
        return result   

    def arch_srv_w_ip():
        result = []
        for service in Service.objects.filter(status=settings.STATUS_ARCHIVED,ifaces__isnull=False):
            result.append({'url':reverse('abonent_services', args=[service.abon.pk]),'title': service.__unicode__() }) 
        return result           

    switch = {'1': dev_wo_location, 
              '2': srv_wo_location, 
              '3':srv_wo_iface, 
              '4':srv_wo_device, 
              '5':arch_srv_w_device,
              '6':arch_srv_w_ip,
              '0':zero }

    menu = {'1': 'Устройства без объекта',
            '2':'Услуги без объекта',
            '3':'Услуги без IP-адреса',
            '4':'Услуги без устройства',
            '5':'Архивные услуги с устройством',
            '6':'Архивные услуги с IP',
            }
    item_list = switch[param]()
    header = menu.get(param)

    return render_to_response('resources/unfilled_params.html', {
                                'menu' : sorted(menu.iteritems()),
                                'header' : header,
                                'item_list' : item_list,
                                },context_instance = RequestContext(request))

@login_required
def abonent_add(request):
    message = u'Добавление нового абонента'
    new = True
    abonent = Abonent()

    if request.method == 'POST':
        form = AbonentForm(request.POST, instance=abonent)
        if form.is_valid():
            newabonent = form.save()
            return HttpResponseRedirect(reverse('abonent_info', args=[newabonent.pk]))
    else:
        form = AbonentForm(instance=abonent)

    return render_to_response('generic/generic_edit.html', { 
                                'header' : message,
                                'form': form,
                                'extend': 'index.html', },
                                 context_instance = RequestContext(request))

@login_required
def smart_search(request):
    abonent_list = Abonent.objects.none()

    if request.method == 'POST': 
        form = SmartSearchForm(request.POST) 
        if form.is_valid():
            string = form.cleaned_data['string']
            request.session['string'] = string
            abonent_list = abonent_filter(string)

    elif request.GET.get('page'): 
        string = request.session['string']  
        abonent_list = abonent_filter(string)
        form = SmartSearchForm()
        form.string = string
    else:
        form = SmartSearchForm()

    paginator = Paginator(abonent_list.distinct(), 10)
    page = request.GET.get('page')
    try:
        abonents = paginator.page(page)
    except PageNotAnInteger:
        abonents = paginator.page(1)
    except EmptyPage:
        abonents = paginator.page(paginator.num_pages)

    return render_to_response('smart_search.html', 
                { 'abonents' : abonents, 
                 'form': form, 
                 'abonent_list_count' : len(abonent_list) }, 
                 context_instance = RequestContext(request))

@login_required
def abonent_search(request):
    abonent_list = []
    if request.method == 'POST': # If the form has been submitted...
        form = AbonentFilterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            contract = form.cleaned_data['contract']
            title = form.cleaned_data['title']
            status = form.cleaned_data['status']
            utype = form.cleaned_data['utype']
            is_credit=form.cleaned_data['is_credit']
            balance_lt=form.cleaned_data['balance_lt']
            balance_gt=form.cleaned_data['balance_gt']
            speed_lt=form.cleaned_data['speed_lt']
            speed_gt=form.cleaned_data['speed_gt']
            tos=form.cleaned_data['tos']
            request.session['contract'] = contract
            request.session['title'] = title
            request.session['status'] = status
            request.session['utype'] = utype
            request.session['is_credit'] = is_credit
            request.session['balance_lt'] = balance_lt
            request.session['balance_gt'] = balance_gt
            request.session['speed_lt'] = speed_lt
            request.session['speed_gt'] = speed_gt
            request.session['tos'] = tos
            abonent_list = Abonent.obj.filter_list(status=status,
                                                    utype=utype,
                                                    is_credit=is_credit,
                                                    balance_lt=balance_lt,
                                                    balance_gt=balance_gt,
                                                    tos=tos,
                                                    title=title,
                                                    contract=contract)
    else:
        form = AbonentFilterForm()

    if request.GET.get('page'):
        abonent_list = Abonent.obj.filter_list(status=request.session['status'],
                                           utype=request.session['utype'],
                                           is_credit=request.session['is_credit'],
                                           balance_lt=request.session['balance_lt'],
                                           balance_gt=request.session['balance_gt'],
                                           speed_lt=request.session['speed_lt'],
                                           speed_gt=request.session['speed_gt'],
                                           tos=request.session['tos'],
                                           title=request.session['title'],
                                           contract=request.session['contract'],)
    paginator = Paginator(abonent_list, 10)

    page = request.GET.get('page')
    try:
        abonents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        abonents = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        abonents = paginator.page(paginator.num_pages)

    return render_to_response('asearch.html', {'form': form, 'abonents' : abonents, 'abonent_list_count' : len(abonent_list) }, context_instance = RequestContext(request) )

# Изменение статуса услуги
@login_required
def service_status_change(request, abonent_id, service_id):
    try:
        # abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404 

    if request.method == 'POST':
        form = ServiceStatusChangesForm(request.POST)
        if form.is_valid(): 
            ssc = form.save(commit=False)
            ssc.service = Service.objects.get(pk=service_id)
            ssc.laststatus = Service.objects.get(pk=service_id).status
            ssc.save()
            return HttpResponseRedirect(reverse('service_status_changes', args=[service.id]))
        else:
            print form.errors
    else:
        form = ServiceStatusChangesForm() 
        # form.fields['plan'].queryset=Plan.objects.filter(tos__pk=tos_id)
        status_list = {settings.STATUS_ACTIVE:[settings.STATUSES[2],settings.STATUSES[4]],
        settings.STATUS_OUT_OF_BALANCE:[settings.STATUSES[2],settings.STATUSES[4]],
        settings.STATUS_PAUSED:[settings.STATUSES[1],settings.STATUSES[4]],
        settings.STATUS_ARCHIVED:[settings.STATUSES[0]],
        settings.STATUS_NEW:[settings.STATUSES[1],settings.STATUSES[4]],}[service.status]

        form.fields['newstatus'].choices = status_list

    return render_to_response('service/service_status_changes.html', {
                                'abonent' : abonent, 
                                'service' : service, 
                                'form': form }, 
                                context_instance = RequestContext(request) )   
# Добававление интерфейса услуги
@login_required
def service_iface_add(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
        # interface = Interface()
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceInterfaceForm(request.POST)
        if form.is_valid():
            iface = form.save()
            service.ifaces.add(iface)
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent.pk]))
    else:
        form = ServiceInterfaceForm()
    
    form.fields['ip'].queryset=IPAddr.objects.filter(net__segment__pk=service.segment.pk,interface=None).filter(net__net_type='UN').filter(net__vlan__in=service.vlan_list.all)

    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': 'Создание нового интерфейса', },
                                 context_instance = RequestContext(request))

# Удаление интерфейса услуги
@login_required
def service_iface_del(request, service_id, iface_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
        interface = Interface.objects.get(pk=iface_id)
    except:
        raise Http404

    interface.delete()

    return HttpResponseRedirect(reverse('abonent_services', args=[abonent.pk]))

# Редактирование интерфейса услуги
@login_required
def service_iface_edit(request, service_id, iface_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
        interface = Interface.objects.get(pk=iface_id)
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceInterfaceForm(request.POST,instance=interface)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent.pk]))
    else:
        form = ServiceInterfaceForm(instance=interface)
        form.fields['ip'].queryset=IPAddr.objects.filter(net__segment__pk=service.segment.pk,interface=None).filter(net__net_type='UN').filter(net__vlan__in=service.vlan_list.all)|IPAddr.objects.filter(interface=interface)

    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': 'Изменение параметров интерфейса',  },
                                 context_instance = RequestContext(request))

# Редактирование статуса услуги
@login_required
def service_state_edit(request, abonent_id, service_id):
    try:
        # abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceStateForm(request.POST,instance=service)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
    else:
        form = ServiceStateForm(instance=service)

    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': 'Принудительная установка статуса',  },
                                 context_instance = RequestContext(request))

# Редактирование оборудования
@login_required
def service_equip_edit(request, abonent_id, service_id):
    try:
        # abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceEquipForm(request.POST,instance=service)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
    else:
        form = ServiceEquipForm(instance=service)
    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': 'Редактирование оборудования',  },
                                 context_instance = RequestContext(request))

# Редактирование скорости услуги
@login_required
def service_speed_edit(request, abonent_id, service_id):
    try:
        # abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceSpeedForm(request.POST,instance=service)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
    else:
        form = ServiceSpeedForm(instance=service)
    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': 'Ручной контроль скорости',  },
                                 context_instance = RequestContext(request))

# Редактирование списка vlan услуги
@login_required
def service_vlan_edit(request, abonent_id, service_id):
    try:
        # abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceVlanForm(request.POST,instance=service)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
    else:
        form = ServiceVlanForm(instance=service)
    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': 'Редактирование спсика Vlan', },
                                 context_instance = RequestContext(request))

# Выбор местоположения услуги
def service_location_choice(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
        header = 'Выбор местоположения услуги'
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceLocationForm(request.POST,instance=service)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent.id]))
    else:
        form = ServiceLocationForm(instance=service)

    breadcrumbs = [({'url':reverse('abonent_services', args=[abonent.id]),'title':'Услуги абонента'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'abonent' : abonent,
                                'breadcrumbs' : breadcrumbs,
                                'form': form,
                                'extend': 'abonent/main.html', },
                                 context_instance = RequestContext(request))

def service_device_release(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        device = service.device
    except:
        raise Http404
    else:
        if device.service_set.all().count()==1:
            device.location = None
            device.save()
            
        service.device = None
        service.save()

    return HttpResponseRedirect(reverse('abonent_services', args=[service.abon.id]))

def service_location_release(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        location = service.location
    except:
        raise Http404
    else:
        service.location = None
        service.save()

    return HttpResponseRedirect(reverse('abonent_services', args=[service.abon.id]))

# Выбор устройства услуги
def service_device_choice(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
        header = 'Выбор абонентского устройства'
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceDeviceForm(request.POST,instance=service)
        if form.is_valid():
            form.save()
            device = service.device
            if not service.location:
                location = Location(bs_type='С',title=service.__unicode__())
                location.save()
                service.location = location
                service.save()
            if form.cleaned_data['change_location']:
                device.location = service.location
                device.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent.id]))
    else:
        form = ServiceDeviceForm(instance=service)
        form.fields['device'].queryset=Device.objects.filter(devtype__category='R',location=None)|\
                                       Device.objects.filter(devtype__category='S')|\
                                       Device.objects.filter(location__bs_type='CP')
        if service.device:
            form.fields['device'].queryset = form.fields['device'].queryset|Device.objects.filter(pk=service.device.pk)
        # else:
        #     form.fields['device'].queryset=Device.objects.filter(location=None)

    breadcrumbs = [({'url':reverse('abonent_services', args=[abonent.id]),'title':'Услуги абонента'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'abonent' : abonent,
                                'breadcrumbs' : breadcrumbs,
                                'form': form,
                                'extend': 'abonent/main.html', },
                                 context_instance = RequestContext(request))

# Редактирование местоположения услуги
@login_required
def service_location_edit(request, abonent_id, service_id):
    try:
        # abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    if request.method == 'POST':
        form = LocationForm(request.POST,instance=service.location)
        if form.is_valid():
            location = form.save()
            service.location = location
            service.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
    else:
        form = LocationForm(instance=service.location)

    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': 'Изменение местоположения',  },
                                 context_instance = RequestContext(request))

# Смена тарифного плана на услуге
@login_required
def service_plan_edit(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    if request.method == 'POST':
        # Выбираем разные формы для юриков и физиков
        if abonent.utype == settings.U_TYPE_FIZ:
            form = ServiceForm(request.POST, instance=service)
            if form.is_valid():
                pass
        else:
            form = OrgServiceForm(request.POST, instance=service)
            if form.is_valid():
                speed = form.cleaned_data['speed']
                price = form.cleaned_data['price']
                install_price = form.cleaned_data['install_price']
                datechange = form.cleaned_data['datechange'] or datetime.now()
                title = u'%s' % (speed)
                # Создаем новый тарифный план
                plan = Plan(title = title,
                            tos = service.tos,
                            speed = speed,
                            comment = 'Автоматически созданный тарифный план',
                            utype = abonent.utype,
                            price = price,
                            install_price = install_price,
                            visible = False)
                plan.save()
                plan.segment.add(service.segment)
                # Создаем запись об назначении тарифного плана
                spc = ServicePlanChanges(
                                service=service,
                                plan=plan,
                                newstatus='A',
                                comment='Изменение тарифного плана',
                                date=datechange)
                spc.save()
                return HttpResponseRedirect(reverse('abonent_services', args=[abonent.id]))
    else:
        if abonent.utype == settings.U_TYPE_FIZ:
            form = ServiceForm(instance=service)
        else:
            form = OrgServiceForm(instance=service)

    return render_to_response('service/service_plan_changes.html', {
                                'form': form,
                                'abonent' : abonent, },
                                context_instance = RequestContext(request)
                                ) 
@login_required
def service_add(request, abonent_id, service_id):
    if service_id == '0':
        message = 'Добавление услуги'
        service = Service()
    else:
        message = 'Изменение услуги'
        service = Service.objects.get(pk=service_id)

    try:
        abonent = Abonent.objects.get(pk = abonent_id)
    except:
        raise Http404

    if request.method == 'POST':
        if abonent.utype == settings.U_TYPE_FIZ:
            form = ServiceForm(request.POST, instance=service)
        else:
            form = OrgServiceForm(request.POST, instance=service)

        if form.is_valid():
            form.save(commit=False)
            service.abon=abonent
            if abonent.utype == settings.U_TYPE_UR:
                speed = form.cleaned_data['speed']
                price = form.cleaned_data['price']
                install_price = form.cleaned_data['install_price']
                datechange = form.cleaned_data['datechange'] or datetime.now()
                title = u'%s' % (speed)

                plan = Plan(title = title,
                            tos = service.tos,
                            speed = speed,
                            comment = 'Автоматически созданный тарифный план',
                            utype = abonent.utype,
                            price = price,
                            install_price = install_price,
                            visible = False)
                plan.save()
                plan.segment.add(service.segment)
                service.plan = plan

            service.save()
            # Создаем запись об назначении тарифного плана
            spc = ServicePlanChanges(
                            service=service,
                            plan=plan,
                            newstatus='A',
                            comment='Изменение тарифного плана',
                            date=datechange)
            spc.save()
            # Создаем запись об активации услуги
            ssc = ServiceStatusChanges(
                            service=service,
                            newstatus=settings.STATUS_ACTIVE,
                            comment='Изменение тарифного плана',
                            date=datechange)
            ssc.save()

            # Создаем уведомление о новой услуге для всех инженеров
            for user in Group.objects.get(name='Инженеры').user_set.all():
                url_abonent = reverse('abonent_info', args=[abonent.pk])
                url_service = reverse('abonent_services', args=[abonent.pk])
                new_note = Note(
                    title = u'Добавлена новая услуга',
                    descr = u"""У абонента <a href=%s>%s</a> добавлена 
                                новая услуга <a href=%s>[%s]</a>. Заполните 
                                технические параметры"""
                                % (url_abonent,abonent.title,url_service,service.pk),
                    marks = 'panel-warning',
                    author = user)
                new_note.save()

            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
    else:
        if abonent.utype == settings.U_TYPE_FIZ:
            form = ServiceForm(instance=service)
        else:
            form = OrgServiceForm(instance=service)

    return render_to_response('service/service_generic_changes.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'menu_title': message, },
                                 context_instance = RequestContext(request))

@login_required	
def abonent_services(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    return render_to_response('service/services.html', { 
                                'abonent' : abonent, 
                                'services' : Service.objects.filter(abon__pk=abonent_id), 
                                's_types' : TypeOfService.objects.all(), }, 
                                context_instance = RequestContext(request))

# Удалить изменение статуса услуги
@login_required   
def ssc_delete(request, ssc_id):
    try:
        ssc = ServiceStatusChanges.objects.get(pk=ssc_id)
        service_id = ssc.service.id
    except:
        raise Http404
    else:
        ssc.delete()

    return HttpResponseRedirect(reverse('service_status_changes', args=[service_id]))

# Удалить изменение тарифного плана
@login_required   
def spc_delete(request, spc_id):
    try:
        spc = ServicePlanChanges.objects.get(pk=spc_id)
        service_id = spc.service.id
    except:
        raise Http404 
    else:
        spc.delete()

    return HttpResponseRedirect(reverse('service_plan_changes', args=[service_id]))

# Изменения статуса услуги
@login_required    
def service_status_changes(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    sscs = ServiceStatusChanges.objects.filter(service__pk=service_id).order_by('-date')
    return render_to_response('service/ssc.html', 
                            { 'abonent' : abonent, 
                              'service' : service,  
                                  'sscs' : sscs, }, 
                                  context_instance = RequestContext(request))

# Изменения тарифа услуги
@login_required    
def service_plan_changes(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    spcs = ServicePlanChanges.objects.filter(service__pk=service_id).order_by('-date')
    return render_to_response('service/spc.html', 
                                { 'abonent' : abonent, 
                                  'service' : service,  
                                     'spcs' : spcs, }, 
                                context_instance = RequestContext(request))

@login_required    
def abonent_history(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    ascs = AbonentStatusChanges.objects.filter(abonent__pk=abonent_id).order_by('-pk')

    return render_to_response('abonent/ssc.html', 
                                { 'abonent' : abonent,
                                     'ascs' : ascs, }, 
                                context_instance = RequestContext(request))

@login_required
def abonent_manage(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    if request.method == 'POST':
        form = ManageForm(request.POST,instance=abonent)
        if form.is_valid():
            tags =  form.cleaned_data['extratag'].split(',')
            abonent.tag = [Tag.objects.get_or_create(title=tag,defaults={'title':tag})[0] for tag in tags]
            # map(lambda tag: abonent.tag.add(Tag.objects.get_or_create(title=tag,defaults={'title':tag})[0]),tags)
            form.save()
    else:
        tag_list = ','.join([tag.title for tag in abonent.tag.all()])
        form = ManageForm(instance=abonent,initial={'extratag': tag_list})

    return render_to_response('generic/generic_edit.html', { 
                                'header' : 'Настройки абонента',
                                'form': form,
                                'abonent': abonent,
                                'extend': 'abonent/main.html', },
                                 context_instance = RequestContext(request))

@login_required    
def abonent_info(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    if abonent.utype == 'F':
        header = 'Паспортные данные'
        template = 'abonent/info_fiz.html'
        data,created = Passport.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'series':'', 'number' : '', 'issued_by' : '', 'date' : datetime.now(), 'address' : '' })
    else:
        header = 'Реквизиты компании'
        template = 'abonent/info_ur.html'
        data,created = Detail.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'title':'', 'inn' : '', 'kpp' : '', 'account' : '', 'post_address' : '', 'official_address' : '' })

    return render_to_response(template, { 
                                'abonent': abonent,
                                'header' : header,
                                'data': data,},
                                 context_instance = RequestContext(request))

@login_required    
def abonent_info_edit(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404
    else:
        if abonent.utype == 'F':
            info, created = Passport.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'series':'', 'number' : '', 'issued_by' : '', 'date' : datetime.now(), 'address' : '' })
            if request.method == 'POST':
                form = PassportForm(request.POST,instance=info)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('abonent_info', args=[abonent.id]))
            else:
                form = PassportForm(instance=info)
            header = 'Паспортные данные'
        else:
            info, created = Detail.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'title':'', 'inn' : '', 'kpp' : '', 'account' : '', 'post_address' : '', 'official_address' : '' })
            if request.method == 'POST':
                form = DetailForm(request.POST,instance=info)
                if form.is_valid():
                    form.save()
                else:
                    print form.errors
            else:
                form = DetailForm(instance=info)
            header = 'Реквизиты компании'

    breadcrumbs = [({'url':reverse('abonent_info', args=[abonent.pk]),'title':header})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'form': form,
                                'breadcrumbs':breadcrumbs,
                                'abonent': abonent,
                                'extend': 'abonent/main.html', },
                                 context_instance = RequestContext(request))

@login_required
def abonent_tts(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        return render_to_response('deadend.html', { 
                                          'message' : u'Абонент не найден', 
                                    'previous_page' : request.META['HTTP_REFERER'] }  , 
                                    context_instance = RequestContext(request))
    
    tts = TroubleTicket.objects.filter(abonent__pk=abonent_id).order_by('-create_date')    
    return render_to_response('abonent/tts.html', { 
                                                    'abonent' : abonent, 
                                                        'tts' : tts, }, 
                              context_instance = RequestContext(request))

def sync_balance_from1C(abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        return 0
    else:        
        s = requests.Session()
        r = s.get('http://agent.albeon.ru:1180/', auth=HTTPDigestAuth('aspekt', 'sapekt123'))

        payload = {'SubscriberID':abonent.contract}
        r = s.get('http://agent.albeon.ru:1180/agent/full_fiz.asp', params=payload, auth=HTTPDigestAuth('aspekt', 'sapekt123'))
        html = r.content.decode('cp1251')
        status_str = u'активен</td>'
        if html.find(status_str)==-1:
            balance_str = u'Баланс: ([-]?\d+[.]?\d*) руб.'
        else:
            balance_str = u'Остаток: ([-]?\d+[.]?\d*) руб.'

        result = re.findall(balance_str, html)
        if len(result):
            balance = float(result[0])

        return balance

def import_abonent_from1C(request):
    db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                             passwd="Aa12345", db="radius", charset='utf8')
    cursor = db.cursor()

    clients = '50______'
    created_list = check_clients(clients,cursor)    # Проверяем нет ли новых абонентов
    for contract in created_list :
        clients = u'%s' % contract
        # period = (datetime.now() - timedelta(hours=24000)).date() # Задаем примерно 3 года
        period = date(2012, 1, 1)          # Лучше с 01.01.2012
        importuntlcdb(cursor,clients,period)        # Проверяем платежи по Uniteller
        importosmp1cdb(cursor,clients,period)       # Проверяем платежи по OSMP
    check_plan(cursor)                              # Проверяем не изменились ли тарифные планы
    check_balance()                                 # Синхронизируем балансы
    db.close()

    url = settings.LOGIN_REDIRECT_URL
    return HttpResponseRedirect(url)

def abonent_settings(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404
    else:   
        setting_list = []
        for service in abonent.service_set.all():
            for iface in service.ifaces.all():
                mask = dec2ip(4294967295 - pow(2,32-iface.ip.net.mask) + 1)
                try:
                    gw = Interface.objects.get(device__router=True,ip__net__pk=iface.ip.net.pk)
                except:
                    gw = 'Шлюз не указан'
                    
                entry = {'location':service.location,'ip': iface.ip.ip, 'mask': mask, 'gw' : gw }
                setting_list.append(entry)

    return render_to_response('abonent/settings.html', { 
                                'abonent': abonent,
                                'settings':setting_list,},
                                 context_instance = RequestContext(request))

def abonent_map(request, abonent_id):
    points = []
    if abonent_id != '0':
        try:
            abonent = Abonent.objects.get(pk=abonent_id)
        except:
            raise Http404
        else:   
            for service in abonent.service_set.all():
                if service.location:
                    if service.location.geolocation:
                        coord = service.location.geolocation
                        lat,lon = coord.split(',')
                        if service.location.address:
                            address = service.location.address
                        else:
                            address = 'Адрес не внесен'
                        comment = """<a href="%s#tr-%s">%s</a>""" % (reverse('abonent_services', args=[service.abon.pk]),service.pk,address)                            
                        entry = {'lat':lat,'lon': lon,'title': address,'comment' :comment } 
                        points.append(entry)
            extend = 'abonent/main.html'
            header = 'Карта услуг абонента'
    else:
        # for location in Location.objects.all():
        for service in Service.objects.all():
            if service.location:
                if service.location.geolocation:
                    coord = service.location.geolocation
                    lat,lon = coord.split(',')
                    comment = """<a href="%s">%s</a>""" % (reverse('abonent_info', args=[service.abon.pk]),service.abon)
                    entry = {'lat':lat,'lon': lon,'title': service.location.address,'comment' : comment} 
                    points.append(entry)
        extend = 'index.html'
        abonent = None
        header = 'Карта абонентов'

    return render_to_response('abonent/map.html', { 
                                'abonent': abonent,
                                'extend' : extend,
                                'header' : header,
                                'points':points,},
                                 context_instance = RequestContext(request))

def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if form.get_user():
                login(request, form.get_user())
                # print request.GET.get('next')
                # user =  form.get_user()
                # Переадресуем в список сообщений, если есть непрочитанные
                if Note.objects.filter(author=request.user,read=False,kind='G').count():
                    url = reverse('notes.views.notes_all')
                else:
                    url = settings.LOGIN_REDIRECT_URL if not request.GET.get('next') else request.GET.get('next')
                return HttpResponseRedirect(url)
    else:
        form = LoginForm()
    return render(request, 'auth.html', {'form': form})

def log_out(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)