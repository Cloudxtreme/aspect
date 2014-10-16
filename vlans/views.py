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
                service = ipaddr.interface.service_set.all()[0]
                service_desc = u'%s - %s' % (service.abon, service.location)
                abon_pk  = service.abon.pk
            except:
                service_desc = u''
                abon_pk = 0

            text['service_desc'] = service_desc
            text['abon_pk'] = abon_pk

            data.append(text)

        return HttpResponse(simplejson.dumps(data))
        json_subcat = serializers.serialize("json", data,fields=('ip',))
    return HttpResponse(json_subcat, mimetype="application/javascript")

@login_required
def vlans_all(request):
    vlan_list = Vlan.objects.all().order_by('number')
    return render_to_response('resources/vlan_list.html', { 'vlan_list': vlan_list }, context_instance = RequestContext(request))

@login_required
def ips(request, parent_id):
	parent_nets = Network.objects.filter(net_type='DN')
	if parent_id == '0':
		net_list = Network.objects.none()
	else:
		net_list = Network.objects.all().filter(parent__pk=parent_id).order_by('decip')
	return render_to_response('ip.html', { 'net_list' : net_list, 'parent_nets' : parent_nets }, context_instance = RequestContext(request))

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
                                'form': form,},
                                context_instance = RequestContext(request)
                                ) 