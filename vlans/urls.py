from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<vlan_id>\d+)/edit/$','vlans.views.vlan_edit', name='vlan_edit'),
    url(r'^all/$', 'vlans.views.vlans_all', name='vlan_all'),
)