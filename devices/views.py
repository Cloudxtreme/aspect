# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from devices.models import Device, DevType, DeviceStatusEntry
from devices.forms import DeviceEditForm
from vlans.models import IPAddr
from django.core import serializers
# import netsnmp
import subprocess

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
    devices_list = Device.objects.all().order_by('ip')
    return render_to_response('devices/devices_list.html', { 'devices_list': devices_list }, context_instance = RequestContext(request))

@login_required
def device_edit(request, device_id=0):
    if device_id != '0' :
        header = 'Редактирование устройства'
        try:
            device = Device.objects.get(pk = device_id)
        except:
            device = Device()
    else:
        header = 'Добавление нового Устройства'
        device = Device()

    if request.method == 'POST':
        form = DeviceEditForm(request.POST, instance=device)
        if form.is_valid():
            newdevice = form.save()
            newdevice.save()
            return HttpResponseRedirect(reverse('devices_all'))
    else:
        form = DeviceEditForm(instance=device)

    template = 'generic/generic_edit.html'
    return render_to_response(template, {
                                'header' : header,
                                'form': form,},
                                context_instance = RequestContext(request)
                                ) 
