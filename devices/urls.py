from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^add_byip/$','devices.views.device_add_byip', name='device_add_byip'),
    url(r'^(?P<device_id>\d+)/edit/$','devices.views.device_edit', name='device_edit'),
    url(r'^(?P<device_id>\d+)/view/$','devices.views.device_view', name='device_view'),
    url(r'^(?P<device_id>\d+)/del/$','devices.views.device_del', name='device_del'),
    url(r'^(?P<device_id>\d+)/save_cfg/$','devices.views.device_save_config', name='device_save_config'),
    url(r'^app/(?P<app_id>\d+)/edit/$','devices.views.app_edit', name='app_edit'),
    url(r'^app/all/$', 'devices.views.apps_all', name='apps_all'),
    url(r'^(?P<device_id>\d+)/auto_attach/$','devices.views.device_auto_attach', name='device_auto_attach'),
    url(r'^(?P<device_id>\d+)/interface/add/$','devices.views.device_iface_add', name='device_iface_add'),
    url(r'^(?P<device_id>\d+)/location/edit/$','devices.views.device_location_edit', name='device_location_edit'),
    url(r'^(?P<device_id>\d+)/location/drop/$','devices.views.device_location_drop', name='device_location_drop'),
    url(r'^(?P<device_id>\d+)/location/choice/(?P<bs>\d+)$','devices.views.device_location_choice', name='device_location_choice'),
    url(r'^(?P<device_id>\d+)/interface/(?P<iface_id>\d+)/edit/$','devices.views.device_iface_edit', name='device_iface_edit'),
    url(r'^interface/(?P<iface_id>\d+)/del/$','devices.views.device_iface_del', name='device_iface_del'),
    url(r'^net/(?P<net_id>\d+)/list$', 'devices.views.devices_list', name='devices_list'),
    url(r'^device_type/(?P<dt_id>\d+)/list$', 'devices.views.devtype_list', name='devtype_list'),
    url(r'^set_state/$', 'devices.views.set_state'),
    url(r'^get_application_entries/$', 'devices.views.get_application_entries',name='get_application_entries'),
    url(r'^get_iparp/$', 'devices.views.get_iparp'),
    url(r'^get_azimuth_info/$', 'devices.views.get_azimuth_info'),
    url(r'^syslog_list/$', 'devices.views.syslog_list', name='syslog_list'),
    url(r'^syslog/(?P<app>\d+)$', 'devices.views.syslog', name='syslog'),
    url(r'^syslog_host/(?P<iface_id>\d+)/$', 'devices.views.syslog_host', name='syslog_host'),
)