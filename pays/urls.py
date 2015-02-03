from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^promisedpays/all$','pays.views.promisedpays_all', name='promisedpays_all'),
    url(r'^quickpay/add$','pays.views.add_quickpayment', name='add_quickpayment'),
    url(r'^all$','pays.views.payments_all', name='payments_all'),
    url(r'^defaulters$','pays.views.get_defaulters', name='defaulters'),
)