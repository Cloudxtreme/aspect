from django.shortcuts import render_to_response
from django.template import RequestContext
from vlans.models import Vlan,IPAddr,Network

# Create your views here.

def vlans_all(request):
    vlan_list = Vlan.objects.all().order_by('number')
    return render_to_response('vlan.html', { 'vlan_list': vlan_list }, context_instance = RequestContext(request))

def ips_all(request):
    ip_list = IPAddr.objects.all().order_by('decip')
    net_list = Network.objects.all().filter(net_type='UN').order_by('decip')
    return render_to_response('ip.html', { 'ip_list': ip_list,'net_list' : net_list }, context_instance = RequestContext(request))
