from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<vlan_id>\d+)/edit/$','vlans.views.vlan_edit', name='vlan_edit'),
    url(r'^all/$', 'vlans.views.vlans_all', name='vlan_all'),
    url(r'^bs_list/$', 'vlans.views.bs_list', name='bs_list'),
    url(r'^bs/(?P<bs_id>\d+)/view/$', 'vlans.views.bs_view', name='bs_view'),
    url(r'^bs/(?P<bs_id>\d+)/edit/$', 'vlans.views.bs_edit', name='bs_edit'),
    url(r'^bs/(?P<bs_id>\d+)/refresh_radio/$', 'vlans.views.refresh_radio', name='refresh_radio'),
    url(r'^create_network/$', 'vlans.views.create_network', name='create_network'),
    url(r'^ipaddr_list/(?P<parent_id>\d+)/$', 'vlans.views.ipaddr_list', name='ips'),
    url(r'^network/(?P<net_id>\d+)/edit/$', 'vlans.views.edit_network', name='edit_network'),
    url(r'^network/(?P<net_id>\d+)/del/$', 'vlans.views.network_del', name='network_del'),
)