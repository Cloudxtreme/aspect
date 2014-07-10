from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^abonent/(?P<abonent_id>\d+)/payments/all$','pays.views.abonent_payments', name='payments'),
    url(r'^abonent/(?P<abonent_id>\d+)/payoffs/all$','pays.views.abonent_payoffs', name='writeoffs'),
    url(r'^abonent/(?P<abonent_id>\d+)/payoffs/add$','pays.views.add_payoff', name='addpayoff'),
    url(r'^abonent/(?P<abonent_id>\d+)/payments/add$','pays.views.add_payment', name='addpayment'),
    url(r'^abonent/(?P<abonent_id>\d+)/promisedpays$','pays.views.promisedpays', name='promisedpays'),
    url(r'^abonent/(?P<abonent_id>\d+)/promisedpays/add$','pays.views.add_promisedpay', name='addpromisedpay'),
    url(r'^abonent/(?P<abonent_id>\d+)/promisedpays/(?P<promisedpay_id>\d+)/close$','pays.views.close_promisedpay', name='closepromisedpay'),
)