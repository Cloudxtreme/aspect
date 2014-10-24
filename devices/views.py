# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from devices.models import Device, DevType, DeviceStatusEntry
from devices.forms import DeviceEditForm, SyslogFilterForm
from users.forms import ServiceInterfaceForm
from users.models import Interface
from vlans.models import IPAddr
from vlans.forms import LocationForm
from django.core import serializers
import MySQLdb
import subprocess
import datetime
from datetime import timedelta

def get_iparp(request):
    ip = request.GET['ip']
    vlan = request.GET['vlan']
    community = 'haser12UMBUNTU'
    router = '10.64.1.14'
    # # oid_str = 'iso.3.6.1.2.1.4.22.1.2.%s.%s' % (vlan,ip)
    # oid_str = 'iso.3.6.1.2.1.4.22.1.2.%s' % (vlan)
    # oid = netsnmp.Varbind(oid_str)
    # result = netsnmp.snmpwalk(oid,
    #                     Version = 2,
    #                     DestHost="192.168.64.1",
    #                     Community="public")

    oid = 'iso.3.6.1.2.1.4.22.1.2.%s.%s' % (vlan,ip)
    cmd = 'snmpwalk -v 2c -c %s %s -OXsq %s' % (community, router, oid)
    PIPE = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=subprocess.STDOUT, close_fds=True, cwd='/home/')
    s = p.stdout.read()
    if s.replace(oid,'').find('No')==-1:
        vlan,ip,mac = s.replace('iso.3.6.1.2.1.4.22.1.2.','').replace('.',' ',1).split(' ',2)
        result = '<div class="alert alert-success" role="alert"><p>Vlan %s</p> <p>IP %s</p> <p>MAC %s</p></div>' % (vlan,ip,mac.replace('"','').replace(' ',':',5))
    else:
        result = '<div class="alert alert-danger" role="alert">ARP запись не обнаружена</div>'        
    return HttpResponse(result)

# @login_required
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
def devices_all(request):
    devices_list = Device.objects.all()

    paginator = Paginator(devices_list.distinct(), 50)
    page = request.GET.get('page')
    try:
        devices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        devices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        devices = paginator.page(paginator.num_pages)

    return render_to_response('devices/devices_list.html', { 'devices': devices }, context_instance = RequestContext(request))

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
            return HttpResponseRedirect(reverse('devices_all'))
    else:
        form = DeviceEditForm(instance=device)

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,},
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
            return HttpResponseRedirect(reverse('devices_all'))
    else:
        form = ServiceInterfaceForm()
    
    if device.router: 
        net_type = ['UN','EN']
        form.fields['ip'].queryset=IPAddr.objects.filter(interface=None).filter(net__net_type__in=net_type)
    else:
        net_type = ['EN']
        form.fields['ip'].queryset=IPAddr.objects.filter(interface=None).filter(net__net_type__in=net_type).filter(net__vlan=device.mgmt_vlan)

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'form': form, },
                                 context_instance = RequestContext(request))

# Удаление интерфейса
@login_required
def device_iface_del(request, iface_id):
    try:
        interface = Interface.objects.get(pk=iface_id)
    except:
        raise Http404

    interface.delete()

    return HttpResponseRedirect(reverse('devices_all'))

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
            return HttpResponseRedirect(reverse('devices_all'))
    else:
        form = ServiceInterfaceForm(instance=interface)
        net_type = ['UN','EN'] if device.router else ['EN']
        form.fields['ip'].queryset=IPAddr.objects.filter(interface=None).filter(net__net_type__in=net_type)|IPAddr.objects.filter(interface=interface)

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'form': form, },
                                 context_instance = RequestContext(request))

# Редактирование местоположения оборудования
@login_required
def device_location_edit(request, device_id):
    try:
        device = Device.objects.get(pk=device_id)
        header = 'Изменение местоположения'
    except:
        raise Http404

    if request.method == 'POST':
        form = LocationForm(request.POST,instance=device.location)
        if form.is_valid():
            location = form.save()
            device.location = location
            device.save()
            return HttpResponseRedirect(reverse('devices_all'))
    else:
        form = LocationForm(instance=device.location)

    return render_to_response('generic/generic_edit.html', { 
                                'header' : header,
                                'form': form, },
                                 context_instance = RequestContext(request))

def syslog_host(request,iface_id):
    log_list = []
    db = MySQLdb.connect(host="192.168.64.6", user="syslog", \
                         passwd="yfpfgbcm", db="syslog", charset='utf8')
    cursor = db.cursor()
    sql = """SELECT * from logs WHERE host='%s' order by `seq` desc limit 150;""" % (Interface.objects.get(pk=iface_id).ip.ip)
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:
        host, facility, priority, level, tag, date, program, msg, seq = rec
        entry = {'host':host, 'msg':msg, 'seq' :seq, 'facility':facility, 'priority':priority, 'level':level, 'tag':tag, 'date':date, 'program':program }
        log_list.append(entry)
    db.close()

    return render_to_response('resources/syslog_list.html', { 'log_list': log_list, },
                                 context_instance = RequestContext(request))    
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
            datefinish = datefinish + timedelta(days=1)
            host = form.cleaned_data['host']
            if host:
                ip = host.ip.ip
                sql = """SELECT * from logs WHERE host='%s'AND datetime >'%s' AND datetime <='%s' order by `seq`;""" % (ip,datestart,datefinish)
                print sql
            else:
                sql = """SELECT * from logs WHERE datetime >'%s' AND datetime <='%s' order by `seq`;""" % (datestart,datefinish)
    else:
        form = SyslogFilterForm()
        sql = """SELECT * from logs order by `seq` desc limit 150;"""
    
    cursor.execute(sql)
    data = cursor.fetchall()
    
    for rec in data:
        host, facility, priority, level, tag, date, program, msg, seq = rec
        entry = {'host':host, 'msg':msg, 'seq' :seq, 'facility':facility, 'priority':priority, 'level':level, 'tag':tag, 'date':date, 'program':program }
        log_list.append(entry)

    db.close()

    return render_to_response('resources/syslog_list.html', { 'log_list': log_list, 'form': form, },
                                 context_instance = RequestContext(request))    