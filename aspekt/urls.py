from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aspekt.views.home', name='home'),
    # url(r'^select2/', include('django_select2.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^pays/', include('pays.urls')),
    url(r'^abonent/', include('users.urls')),
    url(r'^notes/', include('notes.urls')),
    url(r'^notice/', include('notice.urls')), 
    url(r'^tt/', include('tt.urls')),    
    url(r'^contacts/', include('contacts.urls')),
    # url(r'^$', 'vlans.views.index'),
    # url(r'^abonent/(?P<abonent_id>\d+)' ),
    url(r'^login/$', 'users.views.log_in'),
    url(r'^logout/$', 'users.views.log_out'),
    url(r'^vlans/all/$', 'vlans.views.vlans_all'),
    url(r'^ips/(?P<parent_id>\d+)/$', 'vlans.views.ips', name='ips'),
    url(r'^ajax/get_ip/$', 'vlans.views.get_ip'),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^fiziki/$', 'users.views.contact'),
    url(r'^$', 'users.views.abonent_search'),
    # url(r'^ajax/plans/$', 'users.views.feeds_subcatplans'),
    #url(r'^abonent/(?P<abonent_id>\d+)/view/$', 'users.views.abonent_view'),    
    url(r'^asearch/$', 'users.views.aquicksearch', name='aquicksearch'),
    url(r'^reports/plans/$', 'journaling.views.report_plans'),
    url(r'^reports/paysbymonth/$', 'journaling.views.report_paysbymonth'),
    url(r'^reports/paysbyweek/$', 'journaling.views.report_paysbyweek'),
    url(r'^reports/sumbymonth/$', 'journaling.views.report_sumbymonth'),
)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
