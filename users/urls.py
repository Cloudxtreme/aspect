from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
	url(r'^(?P<abonent_id>\d+)/services/$', 
        'users.views.abonent_services', name='abonent_services'),
    # url(r'^abonent/(?P<abonent_id>\d+)/contacts/$','users.views.abonent_contacts'),
    url(r'^(?P<abonent_id>\d+)/statuses/$', 
        'users.views.abonent_history', name='abonent_history'),
    url(r'^(?P<abonent_id>\d+)/tts/$','users.views.abonent_tts'),
    url(r'^(?P<abonent_id>\d+)/info/$','users.views.abonent_info', name='abonent_info'),
    url(r'^(?P<abonent_id>\d+)/manage/$','users.views.abonent_manage', name='abonent_manage'),
    url(r'^(?P<abonent_id>\d+)/services/add/(?P<tos_id>\d+)$', 'users.views.service_add'),
    url(r'^(?P<abonent_id>\d+)/services/(?P<service_id>\d+)/edit/$', 'users.views.service_edit'),
    url(r'^ajax/plans/$', 'users.views.abonent_search'),
    url(r'^ajax/planbytos/$', 'users.views.feeds_plans_by_tos'),
    url(r'^ajax/ipbyseg/$', 'users.views.feeds_ip_by_seg'),
)