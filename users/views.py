# -*- coding: utf-8 -*- 
# from django.shortcuts import render
from django.shortcuts import render_to_response, render, HttpResponseRedirect
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
                         ServiceEquipForm, SmartSearchForm
from journaling.forms import ServiceStatusChangesForm
from notice.forms import AbonentFilterForm
from users.models import Abonent, Service, TypeOfService, Plan, Passport, Detail, Interface, Segment
from tt.models import TroubleTicket, TroubleTicketComment
from journaling.models import ServiceStatusChanges, AbonentStatusChanges
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from vlans.models import Network, IPAddr, Vlan
from vlans.forms import LocationForm
from django.db.models import Avg, Max, Min, Sum, Q
import datetime
import MySQLdb
from django.conf import settings
from pays.models import Payment
from notes.models import Note
from vlans.models import Location
from contacts.models import Contact
from devices.models import dec2ip,ip2dec
import re

def balance(request):
    ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
    
    try:
        balance = '%s руб.' % round((IPAddr.objects.get(ip=ip).interface.service_set.all()[0].abon.balance),2)
    except:
        balance = 'неизвестен'

    return render_to_response('balance.html', {'balance': balance})

@login_required 
def aquicksearch(request):
    data = request.GET
    abonent_list = Abonent.objects.filter(contract__icontains=data['q'])|Abonent.objects.filter(title__icontains=data['q'])|Abonent.objects.filter(detail__title__icontains=data['q'])
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

    if abonent_list.count() == 1:
        return redirect('abonent_info', abonent_id = abonent_list[0].pk) 
    elif abonent_list.count() == 0:
        return render_to_response('deadend.html', { 'message' : u'Абоненты не найдены', 'previous_page' : request.META['HTTP_REFERER'] }  , context_instance = RequestContext(request))
    else:
        return render_to_response('aqsearch_result.html', { 'abonents' : abonents, 'abonent_list_count' : len(abonent_list), 'previous_request' : data['q'] } , context_instance = RequestContext(request))            
        #     return render_to_response('aqsearch_result.html', { 'abonents' : abonents } , context_instance = RequestContext(request))
        
    #return redirect(request.META['HTTP_REFERER'])  

@login_required
def feeds_plans_by_tos(request):
    if request.is_ajax():
        print request.GET['id'], request.GET['seg']
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
        # data = IPAddr.objects.filter(net__segment__pk=request.GET['id'])
        data = IPAddr.objects.filter(net__segment__pk=request.GET['id']).filter(net__net_type='UN').filter(Q(interface=None))|IPAddr.objects.filter(service__pk=request.GET['id'])
        json_subcat = serializers.serialize("json", data)
    return HttpResponse(json_subcat, mimetype="application/javascript")

@login_required
def service_analysis(request):
    internet_services = Service.objects.filter(tos__pk=1,ifaces=None,status__in=['A','N'])
    external_channel = Service.objects.filter(tos__pk=3,vlan_list=None,status__in=['A','N'])
    internal_channel = Service.objects.filter(tos__pk=5)
    # internet_pptp = Service.objects.filter(tos__pk=4)|Service.objects.filter(tos__pk=4,ip=None)

    return render_to_response('service/analysis.html', {
                                'internet_services': internet_services,
                                'external_channel': external_channel,
                                'internal_channel' : internal_channel,
                                # 'internet_pptp' : internet_pptp,
                                },
                                context_instance = RequestContext(request)
                                )  

@login_required
def abonent_add(request,abonent_id=0):
    if abonent_id != '0' :
        message = u'Изменение параметров абонента [%s]' % (abonent_id)
        new = False
        try:
            abonent = Abonent.objects.get(pk = abonent_id)
        except:
            # abonent = Abonent()
            raise Http404
    else:
        message = u'Добавление нового абонента'
        new = True
        abonent = Abonent()

    if request.method == 'POST':
        form = AbonentForm(request.POST, instance=abonent)
        if form.is_valid():
            newabonent = form.save()
            # form.save(commit=False)
            # service.abon=abonent
            # service.save()
            return HttpResponseRedirect(reverse('abonent_info', args=[newabonent.pk]))
        else:
            print form.errors
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
            abonent_list = Abonent.objects.filter(contract__icontains=string)|\
            Abonent.objects.filter(title__icontains=string)|\
            Abonent.objects.filter(detail__title__icontains=string)|\
            Abonent.objects.filter(service__in=Service.objects.filter(location__address__icontains=string))|\
            Abonent.objects.filter(contact__in=Contact.objects.filter(first_name__icontains=string))|\
            Abonent.objects.filter(contact__in=Contact.objects.filter(surname__icontains=string))|\
            Abonent.objects.filter(contact__in=Contact.objects.filter(mobile__icontains=string))
    elif request.GET.get('page'): 
        string = request.session['string']           
        abonent_list = Abonent.objects.filter(contract__icontains=string)|\
        Abonent.objects.filter(title__icontains=string)|\
        Abonent.objects.filter(detail__title__icontains=string)|\
        Abonent.objects.filter(service__in=Service.objects.filter(location__address__icontains=string))|\
        Abonent.objects.filter(contact__in=Contact.objects.filter(first_name__icontains=string))|\
        Abonent.objects.filter(contact__in=Contact.objects.filter(surname__icontains=string))|\
        Abonent.objects.filter(contact__in=Contact.objects.filter(mobile__icontains=string))
        form = SmartSearchForm()
        form.string = string
    else:
        form = SmartSearchForm()

    paginator = Paginator(abonent_list.distinct(), 10)
    page = request.GET.get('page')
    try:
        abonents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        abonents = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        abonents = paginator.page(paginator.num_pages)

    return render_to_response('smart_search.html', { 'abonents' : abonents, 'form': form, 'abonent_list_count' : len(abonent_list.distinct()) }, context_instance = RequestContext(request))

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
        abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
    except:
        raise Http404 

    if request.method == 'POST':
        form = ServiceStatusChangesForm(request.POST)
        if form.is_valid(): 
            ssc = form.save(commit=False)
            ssc.service = Service.objects.get(pk=service_id)
            ssc.laststatus = Service.objects.get(pk=service_id).status
            ssc.save()
            return HttpResponseRedirect(reverse('services_history', args=[abonent_id, service_id]))
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

@login_required
# Смена тарифного плана на услуге
def service_plan_edit(request, abonent_id, service_id):
    try:
        # abonent = Abonent.objects.get(pk = abonent_id)
        service = Service.objects.get(pk=service_id)
        abonent = service.abon
    except:
        raise Http404

    if request.method == 'POST':
        form = ServicePlanForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
    else:
        form = ServicePlanForm(initial={'plan': service.plan})
        form.fields['plan'].queryset=Plan.objects.filter(tos__pk=service.plan.tos.pk, utype=abonent.utype)

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
                datechange = form.cleaned_data['datechange']
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
            # Создаем запись об активации услуги
            if datechange:
                ssc = ServiceStatusChanges(
                                service=service,
                                newstatus=settings.STATUS_ACTIVE,
                                comment='Изменение тарифного плана',
                                date=datechange,
                                # done=True,
                                # successfully=True,
                        )
                ssc.save()
            # Создаем уведомление о новой услуге для всех инженеров
            for user in Group.objects.get(name='Инженеры').user_set.all():
                url_abonent = reverse('abonent_info', args=[abonent.pk])
                url_service = reverse('abonent_services', args=[abonent.pk])
                new_note = Note(
                    title = u'Добавлена новая услуга',
                    descr = u'У абонента <a href=%s>%s</a> добавлена новая услуга <a href=%s>[%s]</a>. Заполните технические параметры' % (url_abonent,abonent.title,url_service,service.pk)  ,
                    marks = 'panel-warning',
                    author = user,
                    )
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

    # return render_to_response('service/service_add.html', {
    #                             'form': form,
    #                             'abonent' : abonent, },
    #                             context_instance = RequestContext(request)
    #                             ) 

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

@login_required   
def ssc_delete(request, abonent_id, service_id, ssc_id):
    ServiceStatusChanges.objects.get(pk=ssc_id).delete()
    return HttpResponseRedirect(reverse('services_history', args=[abonent_id, service_id]))

@login_required    
def service_history(request, abonent_id, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    sscs = ServiceStatusChanges.objects.filter(service__pk=service_id).order_by('-pk')
    return render_to_response('service/history.html', { 'abonent' : abonent, 'service' : service,  'sscs' : sscs, }, context_instance = RequestContext(request))

@login_required    
def abonent_history(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    ascs = AbonentStatusChanges.objects.filter(abonent__pk=abonent_id).order_by('-pk')
    return render_to_response('abonent/history.html', { 'abonent' : abonent,  'ascs' : ascs, }, context_instance = RequestContext(request))

@login_required
def abonent_manage(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    if request.method == 'POST':
        form = ManageForm(request.POST,instance=abonent)
        if form.is_valid():
            form.save()
    else:
        form = ManageForm(instance=abonent)

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
        data,created = Passport.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'series':'', 'number' : '', 'issued_by' : '', 'date' : datetime.datetime.now(), 'address' : '' })
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
            info, created = Passport.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'series':'', 'number' : '', 'issued_by' : '', 'date' : datetime.datetime.now(), 'address' : '' })
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

def import_abonent_from1C(request):
    db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                             passwd="Aa12345", db="radius", charset='utf8')

    cursor = db.cursor()
    sql = """SELECT s.tarif, s.FIO, s.SubscriberID, s.State, s.AddressOfService, s.PasportS, s.PasportN, s.PasportWhon, s.PasportWhen, s.Address, s.Contacts, s.ContactPerson FROM Subscribers AS s, Tarifs as t WHERE s.tarif=t.tarifid AND s.SubscriberID LIKE '50______' AND s.tarif > 1 AND s.FIO!='<b>Фамилия Имя отчество</b>';"""
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:
        plan_id, title, contract, state, address, pass_ser, pass_num, pass_who, pass_when, pass_addr, cnt, prs = rec
        abonent, created = Abonent.objects.get_or_create(contract=contract, defaults={
                          'title' : title,
                          'contract' :contract,
                          'status': 'A' if state else 'N',
                          'utype' :'F',
                          'is_credit' : 'R',
                        })
        created_abon = None
        if created:
            # print u'Создан абонент #%s - %s' % (abonent.contract,abonent.title)
            created_abon = abonent
            try:
                plan = Plan.objects.get(pk=plan_id+1000)
            except:
                pass

            tos = TypeOfService.objects.get(pk=4) # Интернет PPTP id=4
            segment = Segment.objects.get(pk=1) # Основной сегмент
            location = Location(bs_type='C',address=address)
            location.save()
            # Создаем услугу
            service = Service(
                    abon=abonent,
                    tos=tos,
                    segment=segment,
                    location=location,
                    plan=plan,
                    status='A' if state else 'N',
                    )
            service.save()
            # Создаем паспортные данные
            passport = Passport(
                            abonent=abonent,
                            series = pass_ser,
                            number = pass_num,
                            date = pass_when,
                            issued_by = pass_who,
                            address = pass_addr
                            )
            passport.save()
            # Создаем контакт
            r_email = re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)') # Ищем email в строке
            emails = r_email.findall(cnt)

            if emails:
                email = emails[0]
            else:
                email = ''

            if prs == '':
                person = abonent.title # Если имени нет, то берем из тайтла абонента
            else:
                person = prs.decode('cp1251')

            if pass_addr:
                addr = pass_addr
            else:
                addr = ''

            contact = Contact(
                            abonent=abonent,
                            surname=person,
                            address=addr,
                            phone=cnt.decode('cp1251'),
                            email=email,
                  )
            contact.save()

    db.close()
    url = reverse('abonent_info', args=[created_abon.pk]) if created_abon else settings.LOGIN_REDIRECT_URL
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
                gw = Interface.objects.get(device__router=True,ip__net__pk=iface.ip.net.pk)
                entry = {'location':service.location,'ip': iface.ip.ip, 'mask': mask, 'gw' : gw }
                setting_list.append(entry)

    return render_to_response('abonent/settings.html', { 
                                'abonent': abonent,
                                'settings':setting_list,},
                                 context_instance = RequestContext(request))

def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if form.get_user():
                login(request, form.get_user())
                # print request.GET.get('next')
                url = settings.LOGIN_REDIRECT_URL if not request.GET.get('next') else request.GET.get('next')
                return HttpResponseRedirect(url)
    else:
        form = LoginForm()
    return render(request, 'auth.html', {'form': form})

def log_out(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)