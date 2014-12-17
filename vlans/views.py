# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from vlans.models import Vlan, IPAddr, Network
from vlans.forms import VlanEditForm
from django.core import serializers
from django.utils import simplejson

NETWORK_USERS = 'UN'
NETWORK_EQUIP = 'EN'
NETWORK_DISTRIB = 'DN'
NETWORK_LIMITER = 'LN'

TYPE_OF_NETS = (
    (NETWORK_USERS,'Сеть пользователей'),
    (NETWORK_EQUIP,'Сеть оборудование'),
    (NETWORK_DISTRIB,'Сеть для распределения'),
    (NETWORK_LIMITER,'Сеть разделитель'),
)

# def ValuesQuerySetToDict(vqs):
#     return [item for item in vqs]

def get_ip(request):
    if request.GET['id'] == '0':
        json_subcat = serializers.serialize("json", IPAddr.objects.none())
    else:
        # data = IPAddr.objects.filter(net__pk=request.GET['id'])
        data = []
        for ipaddr in IPAddr.objects.filter(net__pk=request.GET['id']):
            text = {
                'ip': ipaddr.ip,
            }

            try:
                if ipaddr.interface.for_device:
                    device = ipaddr.interface.device_set.all()[0]
                    desc = u'%s  %s' % (device.devtype, device.location)
                    anchortag = '#%s' % device.pk
                    url = reverse('devices_list', args=[ipaddr.net.pk]) + anchortag
                else:
                    service = ipaddr.interface.service_set.all()[0]
                    desc = u'%s  %s' % (service.abon, service.location)
                    url = reverse('abonent_info', args=[service.abon.pk])
            except:
                desc = u''
                url = '#'

            text['desc'] = desc
            text['url'] = url

            data.append(text)

        return HttpResponse(simplejson.dumps(data))
        json_subcat = serializers.serialize("json", data,fields=('ip',))
    return HttpResponse(json_subcat, mimetype="application/javascript")

@login_required
def vlans_all(request):
    vlan_list = Vlan.objects.all().order_by('number')
    return render_to_response('resources/vlan_list.html', { 'vlan_list': vlan_list }, context_instance = RequestContext(request))


def dec2ip(ip):
     return '.'.join([str((ip >> 8 * i) & 255) for i in range(3, -1, -1)])
        
def ip2dec(ip):
    return sum([int(q) << i * 8 for i, q in enumerate(reversed(ip.split(".")))])

def calcnet(net,mask):
    mask1 = mask + 1
    net1 = dec2ip(ip2dec(net) + pow(2,31-mask))
    if mask >= 29:
        return (net,mask1),(net1,mask1)
    return (net,mask1),(net1,mask1),calcnet(net,mask1),calcnet(net1,mask1)

@login_required
def ipaddr_list(request, parent_id):
    from itertools import chain
    parent_nets = Network.objects.filter(net_type='DN')
    if parent_id == '0':
        net_list = Network.objects.none()
        result_list = ()
    else:
        nonexsistent_nets = list()
        nonexsistent_nets.append(Network(ip='194.190.13.4',mask=30,net_type='EN',decip=ip2dec('194.190.13.4')))
        nonexsistent_nets.append(Network(ip='194.190.13.24',mask=30,net_type='EN',decip=ip2dec('194.190.13.24')))
        net_list = list(Network.objects.all().filter(parent__pk=parent_id))
        result_list = sorted(
                chain(net_list, nonexsistent_nets),
                key=lambda instance: instance.decip) 

    return render_to_response('ip.html', { 
                                'net_list' : result_list, 
                                'parent_nets' : parent_nets }, 
                                context_instance = RequestContext(request))

@login_required
def vlan_edit(request, vlan_id):
    try:
        vlan = Vlan.objects.get(pk = vlan_id)
        header = 'Редактирование Vlan'
    except:
        vlan = Vlan()
        header = 'Создание нового Vlan'

    if request.method == 'POST':
        form = VlanEditForm(request.POST, instance=vlan)
        if form.is_valid():
            newvlan = form.save()
            newvlan.save()
            return HttpResponseRedirect(reverse('vlan_all'))
    else:
        form = VlanEditForm(instance=vlan)

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 