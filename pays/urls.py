from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^promisedpays/all$','pays.views.promisedpays_all', name='promisedpays_all'),
    url(r'^quickpay/add$','pays.views.add_quickpayment', name='add_quickpayment'),
    url(r'^all$','pays.views.payments_all', name='payments_all'),
    url(r'^defaulters$','pays.views.get_defaulters', name='defaulters'),
    url(r'^abonent/(?P<abonent_id>\d+)/payments$','pays.views.abonent_payments', name='payments'),
    url(r'^abonent/(?P<abonent_id>\d+)/payments/add$','pays.views.add_payment', name='addpayment'),
    url(r'^abonent/(?P<abonent_id>\d+)/payoffs$','pays.views.abonent_payoffs', name='writeoffs'),
    url(r'^abonent/(?P<abonent_id>\d+)/payoffs/add$','pays.views.add_payoff', name='addpayoff'),
    url(r'^abonent/(?P<abonent_id>\d+)/promisedpays$','pays.views.promisedpays', name='promisedpays'),
    url(r'^abonent/(?P<abonent_id>\d+)/promisedpays/add$','pays.views.add_promisedpay', name='addpromisedpay'),
    url(r'^abonent/(?P<abonent_id>\d+)/promisedpays/(?P<promisedpay_id>\d+)/close$','pays.views.close_promisedpay', name='closepromisedpay'),
)