# -*- coding: utf-8 -*- 
from django.shortcuts import render
from django.template import RequestContext
from pays.models import Payment, WriteOff, PromisedPays
from users.models import Abonent, Service
from pays.forms import PaymentForm, WriteOffForm, PromisedPayForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Sum
from django.contrib.auth.models import User

# Create your views here.close_promisedpay
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
	return render(request, 'abonent/add_promisedpay.html', {'form': form, 'abonent' : abonent})

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
def add_payment(request, abonent_id):
	try:
		abonent = Abonent.objects.get(pk=abonent_id)
	except:
		abonent = None

	if request.method == 'POST':
		form = PaymentForm(request.POST)
		if form.is_valid():
			payment = form.save(commit=False)
			payment.abon = abonent
			payment.user = request.user
			payment.save()
			return HttpResponseRedirect(reverse('payments', args=[abonent_id]))
	else:
		form = PaymentForm()
	return render(request, 'abonent/add_payment.html', {'form': form, 'abonent' : abonent})

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
	return render(request, 'abonent/add_payoff.html', {'form': form, 'abonent' : abonent})

@login_required    
def abonent_payments(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
    pays = Payment.objects.filter(abon__pk=abonent_id, valid=True).order_by('-date')    
    pay_stat = Payment.objects.filter(abon__pk=abonent_id, valid=True).aggregate(Avg('sum'), Max('sum'), Min('sum'), Sum('sum'))
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
