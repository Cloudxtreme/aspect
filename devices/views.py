# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from devices.models import Device, DevType, DeviceStatusEntry
from devices.forms import DeviceEditForm
from vlans.models import IPAddr

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
def devices_all(request):
    devices_list = Device.objects.all().order_by('ip')
    return render_to_response('devices/devices_list.html', { 'devices_list': devices_list }, context_instance = RequestContext(request))

@login_required
def device_edit(request, device_id=0):
    if device_id != '0' :
        new = False
        try:
            device = Device.objects.get(pk = device_id)
        except:
            device = Device()
    else:
        new = True
        device = Device()

    if request.method == 'POST':
        form = DeviceEditForm(request.POST, instance=device)
        if form.is_valid():
            newdevice = form.save()
            newdevice.save()
            return HttpResponseRedirect(reverse('devices_all'))
    else:
        form = DeviceEditForm(instance=device)

    return render_to_response('devices/device_edit.html', {
                                'new': new,
                                'form': form,},
                                context_instance = RequestContext(request)
                                ) 
