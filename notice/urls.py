from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^mass_notice_add/$','notice.views.mass_notice_add', name='mass_notice_add'),
    url(r'^abonent/(?P<abonent_id>\d+)/$','notice.views.for_abonent', name='for_abonent'),
    url(r'^abonent/(?P<abonent_id>\d+)/del/(?P<notice_id>\d+)/$','notice.views.notice_email_del', name='notice_email_del'),
    # url(r'^all/performer/(?P<performer_id>\d+)$', 'tt.views.tt_all', name='tt_all'),
)