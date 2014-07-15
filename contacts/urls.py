from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^add/$','contact.views.contact_add', name='contact_add'),
    url(r'^(?P<contact_id>\d+)/del/$','contact.views.contact_del', name='contact_del'),
    url(r'^all/$', 'contact.views.contacts_all', name='contacts_all'),
)