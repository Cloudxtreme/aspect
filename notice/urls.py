from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings 

urlpatterns = patterns('',
    url(r'^mass_notice_add/$','notice.views.mass_notice_add', name='mass_notice_add'),
    url(r'^exec/$','notice.views.notices_exec', name='notices_exec'),
    url(r'^sms/all/send/$','notice.views.sms_all_send', name='sms_all_send'),
    url(r'^create_invoice/$','notice.views.create_invoice', name='create_invoice'),
    url(r'^write_groupemail/$','notice.views.write_groupemail', name='write_groupemail'),
    url(r'^message/(?P<message_id>\d+)/send/$','notice.views.send_message', name='send_message'),
    url(r'^email_all/$','notice.views.email_all', name='email_all'),
    url(r'^sms/all/$','notice.views.sms_all', name='sms_all'),
    url(r'^sms/(?P<sms_id>\d+)/edit/$','notice.views.sms_edit', name='sms_edit'),
    url(r'^sms/(?P<sms_id>\d+)/send/$','notice.views.sms_send', name='sms_send'),
    url(r'^sms/(?P<sms_id>\d+)/del/$','notice.views.sms_del', name='sms_del'),
    url(r'^abonent/(?P<abonent_id>\d+)/del/(?P<notice_id>\d+)/$','notice.views.notice_email_del', name='notice_email_del'),
    url(r'^abonentevents_all/$','notice.views.abonentevents_all', name='abonentevents_all'),
    url(r'^templates_all/$','notice.views.templates_all', name='templates_all'),
    url(r'^emailmessage/(?P<emailmessage_id>\d+)/edit/$','notice.views.emailmessage_edit', name='emailmessage_edit'),
    url(r'^template/(?P<template_id>\d+)/edit/$','notice.views.template_edit', name='template_edit'),
    url(r'^abonentevent/(?P<abonentevent_id>\d+)/edit/$','notice.views.abonentevent_edit', name='abonentevent_edit'),
    url(r'^template/(?P<template_id>\d+)/del/$','notice.views.template_del', name='template_del'),
    url(r'^abonentevent/(?P<abonentevent_id>\d+)/del/$','notice.views.abonentevent_del', name='abonentevent_del'),
    # url(r'^all/performer/(?P<performer_id>\d+)$', 'tt.views.tt_all', name='tt_all'),
)