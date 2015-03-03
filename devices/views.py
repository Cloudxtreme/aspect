# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from devices.models import Device, DevType, DeviceStatusEntry, Application
from devices.forms import DeviceEditForm, SyslogFilterForm, AppEditForm, DeviceChoiceLocationForm, DeviceChoiceServiceForm
from users.forms import ServiceInterfaceForm
from users.models import Interface
from vlans.models import IPAddr, Network
from vlans.forms import LocationForm
from django.core import serializers
import MySQLdb
import subprocess
import datetime
from datetime import timedelta
from django.core import serializers
from django.utils import simplejson
from devices.aux import *

@login_required
def get_iparp(request):
    ip = request.GET['ip']
    vlan = request.GET['vlan']
    try:
        net = IPAddr.objects.get(ip=ip).net
        device = Device.objects.filter(interfaces__ip__net=net,router=True).first()
        router = device.ip.ip if device else '10.64.1.14'
        print device.ip
    except:
        result = '<div class="alert alert-danger" role="alert">Маршрутизатор для этой сети не обнаружен</div>'
    else:
        mac = get_cisco_iparp(ip,vlan,router).upper()
        if mac:
            result = '<div class="alert alert-success" role="alert"><p>Vlan %s</p> <p>IP %s</p> <p>MAC %s</p></div>' % (vlan,ip,mac.replace('"','').replace(' ',':',5))
        else:
            result = '<div class="alert alert-danger" role="alert">ARP запись не обнаружена</div>'

    return HttpResponse(result)

@login_required
def get_azimuth_info(request):
    try:
        device = Device.objects.get(pk=request.GET['id'], devtype__category='R')
    except:
        data ={}
        result = '<div class="alert alert-danger" role="alert">Не поддерживается</div>'
    else:
        result = ''
        if device.location:
            azimuth_list =[]
            distance_list = []
            for peer in device.peers:
                if peer.location:
                    azimuth, distance = azimuth_distance(device.location.geolocation, peer.location.geolocation)
                    azimuth_list.append(azimuth)
                    distance_list.append(distance)

            data = {}
            if azimuth_list:
                data['azimuth_min'] = min(azimuth_list)
                data['azimuth_max'] = max(azimuth_list)
                data['azimuth_angl'] = data['azimuth_max'] - data['azimuth_min']
                data['azimuth_avg'] = sum(azimuth_list)/len(azimuth_list)
                if len(azimuth_list)==1:
                    result += """<p>Направление на станцию %0.2f&deg</p>""" % data['azimuth_min']
                else:
                    result += """<p>Станции лежат в угле %0.2f&deg - %0.2f&deg</p>
                                 <p>Дисперсия %0.2f&deg</p>
                                 <p>Средний угол %0.2f&deg</p>""" % (data['azimuth_min'],data['azimuth_max'],data['azimuth_angl'],data['azimuth_avg'])
            if distance_list:
                data['distance_min'] = min(distance_list)
                data['distance_max'] = max(distance_list)
                data['distance_avg'] = sum(distance_list)/len(distance_list)
                if len(distance_list)==1:
                    result += """<p>Расстояние %0.2f м.</p>""" % data['distance_min']
                else:
                    result += """
                                 <p>Минимальное расстояние %0.2f м</p> 
                                 <p>Максимальное расстояние %0.2f м</p> 
                                 <p>Среднее расстояние %0.2f м</p>""" % (data['distance_min'],data['distance_max'],data['distance_avg'])

    return HttpResponse(result)

@login_required
def detail_delete(request):
    data = {}
    try:
        device = Device.objects.get(pk=request.GET['id'])
        key = request.GET['key']
    except:
        pass
    else:
        device.details_map.pop(key,None)
        device.save()
        data = device.details_map

    return HttpResponse(simplejson.dumps(data))

@login_required
def get_clients(request):
    data = []
    try:
        device = Device.objects.get(pk=request.GET['id'])
        ip = device.ip.ip
        peer_list = device.peers
    except:
        pass
    else:
        data = []
        for mac,signal in get_ubnt_clients(ip):
            text = {}
            try:
                dev = Device.objects.get(interfaces__mac=mac)
            except:
                text['ip'] = ''
                text['url'] = '#'
                text['devname'] = ''
                text['class'] = 'warning'
            else:
                peer_list = peer_list.exclude(pk=dev.pk) if peer_list else []
                ip = dev.ip.ip
                text['devname'] = get_dev_name(ip)
                text['class'] = 'success'
                text['ip'] = ip
                text['url'] = reverse('device_view', args=[dev.pk])
           
            text['mac'] = mac.upper()
            text['signal'] = signal
            data.append(text)    

        for peer in peer_list:
            text = {}
            ip = peer.ip.ip
            text['ip'] = ip
            text['devname'] = get_dev_name(ip)
            text['mac'] = peer.ip.interface.mac
            text['signal'] = '?'
            text['class'] = 'info'
            text['url'] = reverse('device_view', args=[peer.pk])
            data.append(text)

    return HttpResponse(simplejson.dumps(data))

@login_required
def save_config(request):
    data = []
    try:
        device = Device.objects.get(pk=request.GET['id'])
    except:
        pass
    else:
        if device._get_config():
            for config in device.config_set.all()[0:2]:
                text = {}
                text['desc'] = "%s" % config.date
                text['url'] = config.attach.url
                data.append(text)             

    return HttpResponse(simplejson.dumps(data))

@login_required
def get_supply_info(request):
    try:
        snr = Device.objects.get(pk=request.GET['id'], devtype__category='P')
    except:
        data ={}
    else:
        voltage,supply = snr.get_supply_info()
        data = {}
        data['voltage'] = voltage
        data['supply'] = supply
    return HttpResponse(simplejson.dumps(data))

@login_required
def get_radio_param(request):
    ip = dec2ip(int(request.GET['ip']))
    config = get_ubnt_cfg(ip)
    data = {}
    data['freq'] = get_freq_ubnt(config)
    data['width'] = get_width_ubnt(config)
    return HttpResponse(simplejson.dumps(data))

@login_required
def set_state(request):
    ip = request.GET['ip']
    date = request.GET['date']
    title = request.GET['title']
    state = True if request.GET['state']=='up' else False
    devtype = DevType.objects.get(pk=3) # Получаем Unknown device, для заглушки

    try:
        ipaddr = IPAddr.objects.get(ip=ip)
    except IPAddr.DoesNotExist:
        return HttpResponse('IP address not found, create network before')
    
    device, created = Device.objects.get_or_create(ip=ipaddr, 
                        defaults={'title': title,
                                    'ip' : ipaddr, 
                             'mgmt_vlan' : ipaddr.net.vlan,
                               'devtype' : devtype,
                                })

    dse = DeviceStatusEntry(device=device,
                            state_up=state,
                            # date=date
                            )
    dse.save()

    if created:
        return HttpResponse('Device created')
    else:
        return HttpResponse('Device found')

@login_required
def devices_list(request, net_id):
    parent_nets = Network.objects.filter(net_type='EN')
    if net_id == '0':
        dev_list = Device.objects.none()
    elif net_id=='1':
        dev_list = Device.objects.filter(interfaces=None)
    else:
        net = Network.objects.get(pk=net_id)
        # iface_list = net.ipaddr_set.all().values_list('interface')
        # dev_list = Device.objects.filter(interfaces__in=iface_list).order_by('interfaces')
        dev_list = Device.objects.filter(interfaces__ip__net__pk=net_id)

    return render_to_response('devices/devices_list.html', { 
                                'dev_list' : dev_list, 
                                'parent_nets' : parent_nets }, 
                                context_instance = RequestContext(request))

@login_required
def device_view(request, device_id):
    try:
        device = Device.objects.get(pk = device_id)
    except:
        raise Http404

    breadcrumbs = [({'url':reverse('devices_list',args=['0']),'title':'Список оборудования'})]

    return render_to_response('devices/device_view.html', {
                                'device' : device,
                                'breadcrumbs' : breadcrumbs},
                                context_instance = RequestContext(request)
                                )

@login_required
def device_save_config(request, device_id):
    try:
        device = Device.objects.get(pk = device_id)
    except:
        raise Http404

    device._get_config()
    return HttpResponseRedirect(reverse('device_view', args=[device.pk]))
                                           

@login_required
def device_edit(request, device_id):
    try:
        device = Device.objects.get(pk = device_id)
        header = 'Редактирование устройства'
    except:
        device = Device()
        header = 'Добавление нового устройства'

    if request.method == 'POST':
        form = DeviceEditForm(request.POST, instance=device)
        if form.is_valid():
            newdevice = form.save()
            newdevice.save()
            if device.interfaces.all().count():
               net_id = device.interfaces.all()[0].ip.net_id
            else:
                net_id = 1
            anchortag = '#%s' % device.pk
            return HttpResponseRedirect(reverse('devices_list', args=[net_id]) + anchortag)
    else:
        form = DeviceEditForm(instance=device)

    breadcrumbs = [({'url':reverse('devices_list', args=[0]),'title':'Список устройств'})]

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'breadcrumbs' :breadcrumbs,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

# Добававление интерфейса устройства
@login_required
def device_iface_add(request, device_id):
    try:
        device = Device.objects.get(pk=device_id)
        header = 'Создание нового интерфейса'
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceInterfaceForm(request.POST)
        if form.is_valid():
            iface = form.save(commit=False)
            iface.for_device = True
            iface.save()
            device.interfaces.add(iface)
            if device.interfaces.all().count():
               net_id = device.interfaces.all()[0].ip.net_id
            else:
                net_id = 1
            # anchortag = '#%s' % device.pk
            return HttpResponseRedirect(reverse('device_view', args=[device.pk]))
    else:
        form = ServiceInterfaceForm()
    
    if device.router: 
        net_type = ['UN','EN']
        form.fields['ip'].queryset=IPAddr.objects.filter(interface=None).filter(net__net_type__in=net_type)
    else:
        net_type = ['EN']
        form.fields['ip'].queryset=IPAddr.objects.filter(interface=None).filter(net__net_type__in=net_type).filter(net__vlan=device.mgmt_vlan)

    breadcrumbs = [({'url':reverse('device_view', args=[device.pk]),'title':'Просмотр устройства'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'breadcrumbs':breadcrumbs,
                                'form': form,
                                'extend': 'index.html', },
                                 context_instance = RequestContext(request))

# Удаление интерфейса
@login_required
def device_iface_del(request, iface_id):
    try:
        interface = Interface.objects.get(pk=iface_id)
        device_pk = interface.device_set.all().first().pk
    except:
        raise Http404

    interface.delete()
    url = reverse('device_view', args=[device_pk])
    return HttpResponseRedirect(url)

# Редактирование интерфейса
@login_required
def device_iface_edit(request, device_id, iface_id):
    try:
        device = Device.objects.get(pk=device_id)
        interface = Interface.objects.get(pk=iface_id)
        header = 'Редактирование интерфейса'
    except:
        raise Http404

    if request.method == 'POST':
        form = ServiceInterfaceForm(request.POST,instance=interface)
        if form.is_valid():
            form.save()
            if device.interfaces.all().count():
               net_id = device.interfaces.all()[0].ip.net_id
            else:
                net_id = 1
            anchortag = '#%s' % device.pk
            return HttpResponseRedirect(reverse('devices_list', args=[net_id]) + anchortag)
    else:
        form = ServiceInterfaceForm(instance=interface)
        net_type = ['UN','EN'] if device.router else ['EN']
        form.fields['ip'].queryset=IPAddr.objects.filter(interface=None).filter(net__net_type__in=net_type)|IPAddr.objects.filter(interface=interface)

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'form': form, 
                                'extend': 'index.html',},
                                 context_instance = RequestContext(request))
@login_required
def device_location_choice(request, device_id):
    try:
        device = Device.objects.get(pk=device_id)
        header = 'Выбор узла связи'
        if device.interfaces.all().count():
           net_id = device.interfaces.all()[0].ip.net_id
        else:
            net_id = 1
        anchortag = '#%s' % device.pk
    except:
        raise Http404

    if request.method == 'POST':
        form = DeviceChoiceLocationForm(request.POST,instance=device)
        if form.is_valid():
            form.save()
            url = reverse('devices_list', args=[net_id]) + anchortag
            breadcrumbs = [({'url':reverse('bs_view', args=[device.location.pk]),'title':'БС'})]
            message = 'Устройство успешно привязано к БС'
            #return HttpResponseRedirect(url)
    else:
        form = DeviceChoiceLocationForm(instance=device)
        breadcrumbs = []
        message = ''

    breadcrumbs.append({'url':reverse('devices_list', args=[net_id]) + anchortag,'title':'Устройства'})

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'message' : message,
                                'breadcrumbs' : breadcrumbs,
                                'form': form,
                                'extend': 'index.html', },
                                 context_instance = RequestContext(request))


# Редактирование местоположения оборудования
@login_required
def device_location_edit(request, device_id):
    try:
        device = Device.objects.get(pk=device_id)
        header = 'Изменение местоположения'
    except:
        raise Http404

    breadcrumbs = []
    if request.method == 'POST':
        form = LocationForm(request.POST,instance=device.location)
        if form.is_valid():
            location = form.save()
            device.location = location
            device.save()
            net_id = device.ip.net.id if device.ip else 1
            # if device.interfaces.all().count():
            #     net_id = device.interfaces.all()[0].ip.net_id
            # else:
            #     net_id = 1
            anchortag = '#%s' % device.pk
            breadcrumbs = [({'url':reverse('bs_view', args=[device.location.pk]),'title':'БС'})]
            message = 'БС создана успешно'
            # return HttpResponseRedirect(reverse('devices_list', args=[net_id]) + anchortag)
    else:
        form = LocationForm(instance=device.location)
        message = ''   
        net_id = 0

    breadcrumbs.append({'url':reverse('devices_list', args=[net_id]),'title':'Устройства'})

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'message' : message,
                                'breadcrumbs' : breadcrumbs,
                                'form': form,
                                'extend': 'index.html', },
                                 context_instance = RequestContext(request))

# Поиск заявок в журнале на работу с оборудованием по IP адресу
@login_required
def get_application_entries(request):
    if request.GET:
        ipaddr = request.GET['ipaddr']
        app_list = Application.objects.filter(ipaddr__icontains=ipaddr)
    else:
        app_list = Application.objects.none()
    return render_to_response('devices/applications_list.html', { 'app_list': app_list }, context_instance = RequestContext(request))

@login_required
def zapret_info_log(request):
    log_list = []
    db = MySQLdb.connect(host="192.168.64.6", user="syslog", \
                         passwd="yfpfgbcm", db="syslog", charset='utf8')
    cursor = db.cursor()
    sql = """SELECT * from logs WHERE program='zapret_checker.' order by `seq` desc limit 150;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:
        host, facility, priority, level, tag, date, program, msg, seq = rec
        entry = {'host':host, 'msg':msg, 'seq' :seq, 'facility':facility, 'priority':priority, 'level':level, 'tag':tag, 'date':date, 'program':program }
        log_list.append(entry)
    db.close()
    header = u'Журнал получения списка запрещенных сайтов'

    return render_to_response('resources/syslog_list.html', { 'log_list': log_list, 'header' : header },
                                 context_instance = RequestContext(request))

@login_required
def syslog_host(request,iface_id):
    log_list = []
    db = MySQLdb.connect(host="192.168.64.6", user="syslog", \
                         passwd="yfpfgbcm", db="syslog", charset='utf8')
    cursor = db.cursor()
    ip = Interface.objects.get(pk=iface_id).ip.ip
    sql = """SELECT * from logs WHERE host='%s' order by `seq` desc limit 150;""" % (ip)
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:
        host, facility, priority, level, tag, date, program, msg, seq = rec
        entry = {'host':host, 'msg':msg, 'seq' :seq, 'facility':facility, 'priority':priority, 'level':level, 'tag':tag, 'date':date, 'program':program }
        log_list.append(entry)
    db.close()
    header = u'Журнал событий узла %s' % ip

    return render_to_response('resources/syslog_list.html', { 'log_list': log_list, 'header' : header },
                                 context_instance = RequestContext(request))    

@login_required    
def syslog_list(request):
    log_list = []
    db = MySQLdb.connect(host="192.168.64.6", user="syslog", \
                         passwd="yfpfgbcm", db="syslog", charset='utf8')
    cursor = db.cursor()
    if request.method == 'POST':
        form = SyslogFilterForm(request.POST)
        if form.is_valid():
            datestart = form.cleaned_data['datestart']
            datefinish = form.cleaned_data['datefinish']
            host = form.cleaned_data['host']
            conditions = """"""
            if datestart:
                conditions += """AND datetime >'%s'""" % datestart
            if datefinish:
                datefinish = datefinish + timedelta(days=1)
                conditions += """AND datetime <='%s'""" % datefinish
            if host:
                conditions += """AND host='%s'""" % host

            sql = """SELECT * from logs WHERE 1 %s order by `seq`;""" % conditions
    else:
        form = SyslogFilterForm()
        sql = """SELECT * from logs order by `seq` desc limit 50;"""
    
    cursor.execute(sql)
    data = cursor.fetchall()
    
    for rec in data:
        host, facility, priority, level, tag, date, program, msg, seq = rec
        entry = {'host':host, 'msg':msg, 'seq' :seq, 'facility':facility, 'priority':priority, 'level':level, 'tag':tag, 'date':date, 'program':program }
        log_list.append(entry)

    db.close()

    header = u'Журнал syslog'
    return render_to_response('resources/syslog_list.html', { 'log_list': log_list, 'form': form, 'header' : header },
                                 context_instance = RequestContext(request))    


@login_required
def apps_all(request):
    app_list = Application.objects.all().order_by('-date')
    return render_to_response('devices/applications_list.html', { 'app_list': app_list }, context_instance = RequestContext(request))

def get_devbymac(mac):
    return Device.objects.filter(interfaces__mac=mac)

@login_required
def app_edit(request, app_id):
    try:
        app = Application.objects.get(pk = app_id)
        header = u'Редактирование заявки'
    except:
        app = Application()
        header = u'Создание новой заявки'

    if request.method == 'POST':
        form = AppEditForm(request.POST, instance=app)
        if form.is_valid():
            newapp = form.save(commit=False)
            newapp.author = request.user
            newapp.save()
            return HttpResponseRedirect(reverse('apps_all'))
    else:
        form = AppEditForm(instance=app)

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 