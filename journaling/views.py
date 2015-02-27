from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.conf import settings
from django.db.models import Count, Sum
from users.models import Service, Plan, Abonent
from pays.models import Payment

@login_required	
def report_plans(request):
	data = Service.objects.values('plan__speed__speed_in').filter(plan__tos__id=1).order_by('plan__speed__speed_in').annotate(Count('plan__speed__speed_in'))
	total_band = Service.objects.filter(status=settings.STATUS_ACTIVE).aggregate(Sum('plan__speed__speed_in'))['plan__speed__speed_in__sum'] / 1024
	service_count = Service.objects.filter(status=settings.STATUS_ACTIVE).count()
	return render_to_response('stat/report_plans.html', { 'data' : data, 'total_band': total_band, 'service_count' : service_count }, context_instance = RequestContext(request))

@login_required	
def report_paysbymonth(request):
	data = Payment.objects.filter(valid=True,top__stat=True).extra({'weekday': "dayofmonth(date)"}).values('weekday').order_by('weekday').annotate(Count('id'))
	return render_to_response('stat/report_pays.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required
def report_debitsum(request):
	data = Abonent.objects.filter(balance__lt=0,utype='U').aggregate(Sum('balance'))
	return render_to_response('stat/report_debitsum.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required
def report_paysbyweek(request):
	data = Payment.objects.filter(valid=True,top__stat=True).extra({'weekday': "dayofweek(date)" }).values('weekday').order_by('weekday').annotate(Count('id'))
	return render_to_response('stat/report_pays.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required
def report_sumbymonth(request):
	# data = Payment.objects.extra({'month': "dayofweek(date)" }).values('weekday').order_by('weekday').annotate(Count('id'))
	data = Payment.objects.filter(valid=True,top__stat=True).extra(select={'month': 'extract( month from date )',
										 'year': 'extract( year from date )'
										}).values('month','year').order_by('year','month').annotate(dcount=Count('date'),dsum=Sum('summ'))
	return render_to_response('stat/report_sumbymonth.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required	
def report_thrp(request):
	data = Service.objects.extra({'segment': "segment" }).values('plan__speed_in').filter(plan__tos__id=1).order_by('plan__speed_in').annotate(Count('plan__speed_in'))
	return render_to_response('stat/report_thrp.html', { 'data' : data }, context_instance = RequestContext(request))