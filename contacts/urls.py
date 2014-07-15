from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^abonent/(?P<abonent_id>\d+)/edit/(?P<contact_id>\d+)$','contacts.views.contact_edit', name='contact_edit'),
    url(r'^abonent/(?P<abonent_id>\d+)/del/(?P<contact_id>\d+)/$','contacts.views.contact_del', name='contact_del'),
    url(r'^abonent/(?P<abonent_id>\d+)/all/$', 'contacts.views.contacts_all', name='contacts'),
)