from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
	url(r'^(?P<abonent_id>\d+)/services/$', 
        'users.views.abonent_services', name='abonent_services'),
    # url(r'^abonent/(?P<abonent_id>\d+)/contacts/$','users.views.abonent_contacts'),
    url(r'^(?P<abonent_id>\d+)/statuses/$', 
        'users.views.abonent_history', name='abonent_history'),
    url(r'^(?P<abonent_id>\d+)/services/(?P<service_id>\d+)/history/$', 
        'users.views.service_history', name='services_history'),
    url(r'^(?P<abonent_id>\d+)/services/(?P<service_id>\d+)/ssc/(?P<ssc_id>\d+)/delete/$',
        'users.views.ssc_delete', name='ssc_delete'),
    url(r'^(?P<abonent_id>\d+)/tts/$','users.views.abonent_tts'),
    url(r'^(?P<abonent_id>\d+)/info/$','users.views.abonent_info', name='abonent_info'),
    url(r'^(?P<abonent_id>\d+)/manage/$','users.views.abonent_manage', name='abonent_manage'),
    url(r'^(?P<abonent_id>\d+)/services/add/(?P<tos_id>\d+)$', 'users.views.service_add'),
    url(r'^(?P<abonent_id>\d+)/services/(?P<service_id>\d+)/edit/$', 'users.views.service_edit'),
    url(r'^(?P<abonent_id>\d+)/tts/(?P<tt_id>\d+)/edit/$', 'tt.views.tt_add', name='tt_add'),
    url(r'^(?P<abonent_id>\d+)/tts/(?P<tt_id>\d+)/comment_add/$', 'tt.views.tt_comment_add', name='tt_comment_add'),
    url(r'^(?P<abonent_id>\d+)/services/(?P<service_id>\d+)/status_change/$', 'users.views.service_status_change'),
    url(r'^(?P<abonent_id>\d+)/add/$', 'users.views.abonent_add'),
    url(r'^ajax/plans/$', 'users.views.abonent_search'),
    url(r'^ajax/planbytos/$', 'users.views.feeds_plans_by_tos'),
    url(r'^ajax/ipbyseg/$', 'users.views.feeds_ip_by_seg'),
)