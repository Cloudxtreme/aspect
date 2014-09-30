from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<device_id>\d+)/edit/$','devices.views.device_edit', name='device_edit'),
    url(r'^all/$', 'devices.views.devices_all', name='devices_all'),
    url(r'^set_state/$', 'devices.views.set_state'),
)