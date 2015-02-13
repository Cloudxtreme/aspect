# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from vlans.models import Vlan, IPAddr, Network, Location
from vlans.forms import VlanEditForm, NetworkForm, LocationForm
from users.models import Segment
from django.core import serializers
from django.utils import simplejson
from devices.aux import dec2ip,ip2dec
from devices.models import Device

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

@login_required
def network_del(request,net_id):
    try:
        net = Network.objects.get(pk=net_id)
    except:
        raise Http404

    parent_id = net.parent_id
    net.delete()

    return HttpResponseRedirect(reverse('ips', args=[parent_id]))    


@login_required
def edit_network(request,net_id):
    try:
        net = Network.objects.get(pk=net_id)
    except:
        raise Http404

    if request.method == 'POST':
        form = NetworkForm(request.POST,instance=net)
        if form.is_valid():
            network = form.save()
            return HttpResponseRedirect(reverse('ips', args=[network.parent_id]))
    else:
        form = NetworkForm(instance=net)

    message = 'Редактирование подсети'

    breadcrumbs = [({'url':reverse('ips', args=[net.parent_id]),'title':'Список сетей'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : message,
                                'breadcrumbs':breadcrumbs,
                                'form': form,
                                'extend': 'index.html', },
                                 context_instance = RequestContext(request))        

@login_required
def create_network(request):
    if request.method == 'GET':
        decip = int(request.GET['ip'])
        mask = request.GET['mask']
        net = Network(ip=dec2ip(decip),mask=mask,decip=decip)
        form = NetworkForm(instance=net)
    elif request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            newnetwork = form.save(commit=False)
            newnetwork.segment = Segment.objects.get(pk=1)
            newnetwork.save()
            return HttpResponseRedirect(reverse('ips', args=[newnetwork.parent_id]))
    else:
        form = NetworkForm()

    message = 'Создание подсети'    
    breadcrumbs = [({'url':reverse('ips', args=[0]),'title':'Список сетей'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : message,
                                'breadcrumbs':breadcrumbs,
                                'form': form,
                                'extend': 'index.html', },
                                 context_instance = RequestContext(request))



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

def gen_nets(parent_id):
    net_ip = Network.objects.get(pk=parent_id).ip
    mask = Network.objects.get(pk=parent_id).mask

    net_list = []
    for net in Network.objects.all().filter(parent__pk=parent_id):
        entry = (ip2dec(net.ip),ip2dec(net.ip)+pow(2,32-net.mask)-1)
        net_list.append(entry)

    # net_list = nets_range(parent_id)
    result = []

    for ip in range(ip2dec(net_ip),ip2dec(net_ip)+pow(2,32-mask)-1):
        for i in range(2 if mask >=22 else 8,32-mask):
            if not (ip % pow(2,i)):
                colission = False
                for first_addr,last_addr in net_list:
                    if (ip > last_addr) or (ip+pow(2,i)-1 < first_addr):
                        colission = False
                    else:
                        colission = True
                        break
                if not colission:
                    # print '%s/%s' % (ip,32-i)
                    result.append((dec2ip(ip),32-i))
            else:
                break
    
    return result

@login_required
def ipaddr_list(request, parent_id):
    from itertools import chain
    parent_nets = Network.objects.filter(net_type='DN')
    if parent_id == '0':
        net_list = Network.objects.none()
        result_list = ()
    else:
        nonexsistent_nets = list()
        for ip,mask in gen_nets(parent_id):
            nonexsistent_nets.append(Network(ip=ip,mask=mask,net_type='EN',decip=ip2dec(ip)))  
        net_list = list(Network.objects.all().filter(parent__pk=parent_id))
        result_list = sorted(
                chain(net_list, nonexsistent_nets),
                key=lambda instance: instance.decip + instance.mask * 0.01 ) 

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

    breadcrumbs = [({'url':reverse('vlan_all',),'title':'Список вланов'})]

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,
                                'breadcrumbs':breadcrumbs,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

# Список всех БС
@login_required
def bs_list(request):
    bs_list = Location.objects.filter(bs_type='B').order_by('pk')
    return render_to_response('bs_list.html', { 'bs_list': bs_list }, context_instance = RequestContext(request))


# Просмотр БС
@login_required
def bs_view(request,bs_id):
    try:
        bs = Location.objects.get(pk = bs_id)
    except:
        raise Http404
    
    device_list = Device.objects.filter(location=bs)

    breadcrumbs = [({'url':reverse('bs_list',),'title':'Список БС'})]

    return render_to_response('bs_view.html', 
                                { 'bs': bs, 
                                'header' : bs.address,
                                'breadcrumbs' : breadcrumbs,
                                'device_list' : device_list }, 
                                context_instance = RequestContext(request))
@login_required
def refresh_radio(request,bs_id):
    try:
        bs = Location.objects.get(pk = bs_id)
    except:
        raise Http404
    
    for device in Device.objects.filter(location=bs):
        device._refresh_radio()
    
    return HttpResponseRedirect(reverse('bs_view',args=[bs_id]))

# Редактирование местоположения
@login_required
def bs_edit(request, bs_id):
    try:
        bs = Location.objects.get(pk=bs_id)
    except:
        bs = Location()

    if request.method == 'POST':
        form = LocationForm(request.POST,instance=bs)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('bs_list'))
    else:
        form = LocationForm(instance=bs)

    breadcrumbs = [({'url':reverse('bs_list',),'title':'Список БС'}),({'url':reverse('bs_view',args=[bs_id]),'title':'Просмотр БС'})]

    return render_to_response('generic/generic_edit.html', {
                                'form': form,
                                'breadcrumbs':breadcrumbs,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 