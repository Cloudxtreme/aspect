# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from devices.models import Device
from devices.forms import DeviceEditForm

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
