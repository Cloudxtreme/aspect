from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Count, Sum
from users.models import Service, Plan, Abonent
from pays.models import Payment

@login_required	
def report_plans(request):
	data = Service.objects.values('plan__speed__speed_in').filter(plan__tos__id=1).order_by('plan__speed__speed_in').annotate(Count('plan__speed__speed_in'))
	return render_to_response('report_plans.html', { 'data' : data, 'service_count' : Service.objects.all().count }, context_instance = RequestContext(request))

@login_required	
def report_paysbymonth(request):
	data = Payment.objects.filter(valid=True,top__stat=True).extra({'weekday': "dayofmonth(date)"}).values('weekday').order_by('weekday').annotate(Count('id'))
	return render_to_response('report_paysbymonth.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required
def report_debitsum(request):
	data = Abonent.objects.filter(balance__lt=0,utype='U').aggregate(Sum('balance'))
	return render_to_response('report_debitsum.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required
def report_paysbyweek(request):
	data = Payment.objects.filter(valid=True,top__stat=True).extra({'weekday': "dayofweek(date)" }).values('weekday').order_by('weekday').annotate(Count('id'))
	return render_to_response('report_paysbyweek.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required
def report_sumbymonth(request):
	# data = Payment.objects.extra({'month': "dayofweek(date)" }).values('weekday').order_by('weekday').annotate(Count('id'))
	data = Payment.objects.filter(valid=True,top__stat=True).extra(select={'month': 'extract( month from date )',
										 'year': 'extract( year from date )'
										}).values('month','year').order_by('year','month').annotate(dcount=Count('date'),dsum=Sum('sum'))
	return render_to_response('report_sumbymonth.html', { 'data' : data }, context_instance = RequestContext(request))

@login_required	
def report_thrp(request):
	data = Service.objects.extra({'segment': "segment" }).values('plan__speed_in').filter(plan__tos__id=1).order_by('plan__speed_in').annotate(Count('plan__speed_in'))
	return render_to_response('report_thrp.html', { 'data' : data }, context_instance = RequestContext(request))