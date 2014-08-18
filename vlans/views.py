# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext
from vlans.models import Vlan, IPAddr, Network
from django.core import serializers

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
        data = IPAddr.objects.filter(net__pk=request.GET['id']).only('pk','ip','service__abon','service__abon__id')
        # data = IPAddr.objects.filter(net__pk=request.GET['id'])
        # data_dict = ValuesQuerySetToDict(data)
        # print IPAddr.objects.filter(net__pk=request.GET['id']).values('id','ip','service__abon__title','service__abon__pk')
        json_subcat = serializers.serialize("json", data)
            # , indent=3, relations=('service',))
    return HttpResponse(json_subcat, mimetype="application/javascript")

def vlans_all(request):
    vlan_list = Vlan.objects.all().order_by('number')
    return render_to_response('vlan.html', { 'vlan_list': vlan_list }, context_instance = RequestContext(request))

def ips(request, parent_id):
	parent_nets = Network.objects.filter(net_type='DN')
	if parent_id == '0':
		net_list = Network.objects.none()
	else:
		net_list = Network.objects.all().filter(parent__pk=parent_id).order_by('decip')
	return render_to_response('ip.html', { 'net_list' : net_list, 'parent_nets' : parent_nets }, context_instance = RequestContext(request))
