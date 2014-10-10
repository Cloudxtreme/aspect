from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^mass_notice_add/$','notice.views.mass_notice_add', name='mass_notice_add'),
    url(r'^exec/$','notice.views.notices_exec', name='notices_exec'),
    url(r'^write_groupemail/$','notice.views.write_groupemail', name='write_groupemail'),
    url(r'^abonent/(?P<abonent_id>\d+)/$','notice.views.for_abonent', name='for_abonent'),
    url(r'^email_all/$','notice.views.email_all', name='email_all'),
    url(r'^abonent/(?P<abonent_id>\d+)/del/(?P<notice_id>\d+)/$','notice.views.notice_email_del', name='notice_email_del'),
    url(r'^abonentevents_all/$','notice.views.abonentevents_all', name='abonentevents_all'),
    url(r'^templates_all/$','notice.views.templates_all', name='templates_all'),
    url(r'^template/(?P<template_id>\d+)/edit/$','notice.views.template_edit', name='template_edit'),
    url(r'^abonentevent/(?P<abonentevent_id>\d+)/edit/$','notice.views.abonentevent_edit', name='abonentevent_edit'),
    url(r'^template/(?P<template_id>\d+)/del/$','notice.views.template_del', name='template_del'),
    url(r'^abonentevent/(?P<abonentevent_id>\d+)/del/$','notice.views.abonentevent_del', name='abonentevent_del'),
    # url(r'^all/performer/(?P<performer_id>\d+)$', 'tt.views.tt_all', name='tt_all'),
)