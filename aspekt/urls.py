from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aspekt.views.home', name='home'),
    # url(r'^select2/', include('django_select2.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^pays/', include('pays.urls')),
    url(r'^abonent/', include('users.urls')),
    url(r'^notes/', include('notes.urls')),
    url(r'^notice/', include('notice.urls')), 
    url(r'^tt/', include('tt.urls')),    
    url(r'^contacts/', include('contacts.urls')),
    url(r'^vlans/', include('vlans.urls')),
    url(r'^devices/', include('devices.urls')),
    url(r'^login/$', 'users.views.log_in'),
    url(r'^logout/$', 'users.views.log_out'),
    url(r'^ajax/get_ip/$', 'vlans.views.get_ip'),
    url(r'^ajax/run_ipscanner/$', 'devices.views.run_ipscanner', name='run_ipscanner'),
    url(r'^ajax/get_ipscanner_state/$', 'devices.views.get_ipscanner_state',name='get_ipscanner_state'),
    url(r'^ajax/get_radio_param/$', 'devices.views.get_radio_param'),
    url(r'^ajax/get_supply_info/$', 'devices.views.get_supply_info'),
    url(r'^ajax/save_config/$', 'devices.views.save_config'),
    url(r'^ajax/detail_delete/$', 'devices.views.detail_delete'),
    url(r'^ajax/get_clients/$', 'devices.views.get_clients'),
    url(r'^$', 'users.views.smart_search'),
    url(r'^asearch/$', 'users.views.aquicksearch', name='aquicksearch'),
    url(r'^smartsearch/$', 'users.views.smart_search', name='smart_search'),
    url(r'^zapret/$', 'users.views.zapret', name='zapret'),
    url(r'^reports/plans/$', 'journaling.views.report_plans'),
    url(r'^reports/paysbymonth/$', 'journaling.views.report_paysbymonth'),
    url(r'^reports/paysbyweek/$', 'journaling.views.report_paysbyweek'),
    url(r'^reports/sumbymonth/$', 'journaling.views.report_sumbymonth'),
    url(r'^reports/debitsum/$', 'journaling.views.report_debitsum'),
)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
