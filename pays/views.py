# -*- coding: utf-8 -*- 
from django.shortcuts import render
from django.template import RequestContext
from pays.models import Payment, WriteOff, PromisedPays, PaymentSystem
from users.models import Abonent, Service
from pays.forms import PaymentForm, WriteOffForm, PromisedPayForm,QuickPaymentForm, DateChoiceForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Sum
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.conf import settings

# Create your views here.close_promisedpay

@login_required
def get_defaulters(request):
    today = datetime.now()
    abonent_list = []
    for abonent in Abonent.objects.filter(status=settings.STATUS_OUT_OF_BALANCE):
        if abonent.payment_set.all().count() > 0:
            if today - abonent.payment_set.all().order_by('-date')[0].date > timedelta(days=180):
                abonent_list.append(abonent) 

    return render_to_response('aqsearch_result.html', { 'abonents' : abonent_list, 'abonent_list_count' : len(abonent_list) } , context_instance = RequestContext(request))

@login_required
def close_promisedpay(request, abonent_id, promisedpay_id):
	PromisedPays.objects.get(pk=promisedpay_id).close()
	return HttpResponseRedirect(reverse('promisedpays', args=[abonent_id]))

@login_required
def add_promisedpay(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None

    if request.method == 'POST':
        form = PromisedPayForm(request.POST)
        if form.is_valid():
            promisedpay = form.save(commit=False)
            promisedpay.abonent = abonent
            promisedpay.user = request.user
            promisedpay.save()
            return HttpResponseRedirect(reverse('promisedpays', args=[abonent_id]))
    else:
        form = PromisedPayForm(initial={'summ': round(abs(0 - abonent.balance),2) })
    # return render(request, 'abonent/add_promisedpay.html', {'form': form, 'abonent' : abonent})

    breadcrumbs = [({'url':reverse('promisedpays', args=[abonent.pk]),'title':'Обещанные платежи'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : 'Обещанный платеж',
                                'form': form,
                                'breadcrumbs':breadcrumbs,
                                'abonent': abonent,
                                'extend': 'abonent/main.html', },
                                 context_instance = RequestContext(request))


@login_required
def payments_all(request):
    payments_list = Payment.objects.none()
    if request.method == 'POST':
        form = DateChoiceForm(request.POST)
        if form.is_valid():
            datestart = form.cleaned_data['datestart']
            datefinish = form.cleaned_data['datefinish']
            paymentsystem = form.cleaned_data['paymentsystem']
            utype = form.cleaned_data['utype']
            datefinish = datefinish + timedelta(days=1)
            payments_list = Payment.obj.filter_list(datestart=datestart,
                                                    datefinish=datefinish,
                                                    top=paymentsystem,
                                                    utype=utype)
    else:
        form = DateChoiceForm()

    return render_to_response('payments_all.html', { 
                                'payments_list' : payments_list,
                                'summ' : payments_list.aggregate(Sum('summ'))['summ__sum'],
                                'form' : form }, 
                                context_instance = RequestContext(request))

@login_required
def promisedpays_all(request):
    promisedpays_list = PromisedPays.objects.filter(pay_onaccount=True).order_by('-pk')    

    return render_to_response('promisedpays_all.html', { 
                                'promisedpays_list' : promisedpays_list, }, 
                              context_instance = RequestContext(request))

@login_required
def promisedpays(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
    promisedpays = PromisedPays.objects.filter(abonent__pk=abonent_id).order_by('-pk')    

    return render_to_response('abonent/promised_pays.html', { 
                                'abonent' : abonent, 
                                'promisedpays' : promisedpays, 
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() }, 
                              context_instance = RequestContext(request))

@login_required
def add_quickpayment(request):
    message = ''
    if request.method == 'POST':
        form = QuickPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.top = PaymentSystem.objects.get(pk=3)
            payment.user = request.user
            payment.save()
            message  = "Платеж на сумму %s руб для %s зачислен" % (payment.summ, payment.abonent)
            form = QuickPaymentForm()
        else:
            message = "Ошибки в форме"
    else:
        form = QuickPaymentForm()
        header = 'Данные платежа'

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'message' : message,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

@login_required
def add_payment(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.abonent = abonent
            payment.user = request.user
            payment.save()
            return HttpResponseRedirect(reverse('payments', args=[abonent_id]))
    else:
        form = PaymentForm()

    # return render(request, 'abonent/add_payment.html', {'form': form, 'abonent' : abonent})
    breadcrumbs = [({'url':reverse('payments', args=[abonent.pk]),'title':'Список платежей'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : 'Добавление платежа',
                                'form': form,
                                'breadcrumbs':breadcrumbs,
                                'abonent': abonent,
                                'extend': 'abonent/main.html', },
                                 context_instance = RequestContext(request))
@login_required
def add_payoff(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None	

    if request.method == 'POST':
        form = WriteOffForm(request.POST)
        if form.is_valid():
            # form.save()
            payoff = form.save(commit=False)
            payoff.abonent = abonent
            payoff.user = request.user
            payoff.save()
            return HttpResponseRedirect(reverse('writeoffs', args=[abonent_id]))
    else:
        form = WriteOffForm()
        form.fields['service'].queryset=Service.objects.filter(abon__pk=abonent_id)

    # return render(request, 'abonent/add_payoff.html', {'form': form, 'abonent' : abonent})
    breadcrumbs = [({'url':reverse('writeoffs', args=[abonent.pk]),'title':'Список списаний'})]

    return render_to_response('generic/generic_edit.html', { 
                                'header' : 'Списать средства',
                                'form': form,
                                'breadcrumbs':breadcrumbs,
                                'abonent': abonent,
                                'extend': 'abonent/main.html', },
                                 context_instance = RequestContext(request))    

@login_required    
def abonent_payments(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
    pays = Payment.objects.filter(abonent__pk=abonent_id, valid=True).order_by('-date')    
    pay_stat = Payment.objects.filter(abonent__pk=abonent_id, valid=True).aggregate(Avg('summ'), Max('summ'), Min('summ'), Sum('summ'))
    return render_to_response('abonent/pays.html', {
                                'abonent' : abonent,
                                'pays' : pays,
                                'pay_stat' : pay_stat,
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() }, 
                              context_instance = RequestContext(request))

@login_required    
def abonent_payoffs(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
    payoffs = WriteOff.objects.filter(abonent__pk=abonent_id, valid=True).order_by('-date')    
    return render_to_response('abonent/payoffs.html', { 
                                'abonent' : abonent, 
                                'payoffs' : payoffs, 
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() }, 
                              context_instance = RequestContext(request))
