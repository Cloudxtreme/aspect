# -*- coding: utf-8 -*- 
# from django.shortcuts import render
from django.shortcuts import render_to_response, render, HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.core import serializers
# from django.views.decorators.csrf import csrf_exempt, csrf_protect
# from django.core.context_processors import csrf
from django.template import RequestContext
from users.forms import  ServiceForm, SearchForm, LoginForm, PassportForm, DetailForm, ManageForm
# from vlans.forms import LocationForm
from users.models import Abonent, Service, TypeOfService, Plan, Passport, Detail
from tt.models import TroubleTicket, TroubleTicketComment
from vlans.models import Network, IPAddr
from journaling.models import AbonentStatusChanges
from django.db.models import Avg, Max, Min, Sum, Q
import datetime

from pays.models import Payment

@login_required
def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('#') # Redirect after POST
    else:
        form = AbonentForm() # An unbound form

    return render_to_response('fizik.html', {
        'form': form,
    }, context_instance = RequestContext(request))

@login_required	
def aquicksearch(request):
    if request.method == 'POST': # If the form has been submitted...
        data = request.POST
        abonents = Abonent.objects.filter(contract__icontains=data['q'])
        if abonents.count() == 1:
            return redirect('abonent_info', abonent_id = abonents[0].pk) 
        elif abonents.count() == 0:
            return render_to_response('deadend.html', { 'message' : u'Абоненты не найдены', 'previous_page' : request.META['HTTP_REFERER'] }  , context_instance = RequestContext(request))
        else:
            return render_to_response('aqsearch_result.html', { 'abonents' : abonents } , context_instance = RequestContext(request))
    #return redirect(request.META['HTTP_REFERER'])        

@login_required
def feeds_plans_by_tos(request):
    if request.is_ajax():
        print request.GET['id'], request.GET['seg']
        if request.GET['id'] == '0' or request.GET['seg'] == '0':
            json_subcat = serializers.serialize("json", Plan.objects.none())
        else:
            json_subcat = serializers.serialize("json", Plan.objects.filter(tos__pk=request.GET['id'],segment__pk=request.GET['seg']))
        return HttpResponse(json_subcat, mimetype="application/javascript")
    else:
        form = ServiceForm() # An unbound form
        return render_to_response('asearch.html', {'form': form} )

@login_required
def feeds_ip_by_seg(request):
    if request.GET['id'] == '0':
        json_subcat = serializers.serialize("json", IPAddr.objects.none())
    else:
        data = IPAddr.objects.filter(net__segment__pk=request.GET['id'])
        json_subcat = serializers.serialize("json", data)
    return HttpResponse(json_subcat, mimetype="application/javascript")

# def feeds_subcatplans(request):
#     if request.is_ajax():
#         if request.GET['id'] == '0':
#             json_subcat = serializers.serialize("json", Plan.objects.all())
#         else:
#             json_subcat = serializers.serialize("json", Plan.objects.filter(tos__pk=request.GET['id']))
#         return HttpResponse(json_subcat, mimetype="application/javascript")
#     else:
#         form = SearchForm() # An unbound form
#         return render_to_response('asearch.html', {'form': form} )

@login_required
def abonent_search(request):
    if request.is_ajax():
        if request.GET['id'] == '0':
            json_subcat = serializers.serialize("json", Plan.objects.all())
        else:
            json_subcat = serializers.serialize("json", Plan.objects.filter(tos__pk=request.GET['id']))
        return HttpResponse(json_subcat, mimetype="application/javascript")

    if request.method == 'POST': # If the form has been submitted...
        form = SearchForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('#') # Redirect after POST
    else:
        form = SearchForm() # An unbound form
    return render_to_response('asearch.html', {'form': form }, context_instance = RequestContext(request) )

@login_required
def service_add(request, abonent_id="0", tos_id="0"):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid(): 
            newservice = form.save(commit=False)
            newservice.abon = Abonent.objects.get(pk=abonent_id)
            newservice.save()
        else:
            print form.errors
    else:
        form = ServiceForm() 
        form.fields['plan'].queryset=Plan.objects.filter(tos__pk=tos_id)
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent, services = None	
    return render_to_response('abonent/srv_edit.html', {
                                'abonent' : abonent, 
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), 
                                'form': form }, 
                                context_instance = RequestContext(request) )    

@login_required
def service_edit(request, abonent_id, service_id=0):
    if service_id != '0' :
        message = u'Изменение параметров услуги [%s]' % (service_id)
        new = False
        service = Service.objects.get(pk=service_id)
    else:
        message = u'Добавление новой услуги'
        new = True
        service = Service()

    try:
        abonent = Abonent.objects.get(pk = abonent_id)
    except:
        abonent = None

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save(commit=False)
            service.abon=abonent
            service.save()
            return HttpResponseRedirect(reverse('abonent_services', args=[abonent_id]))
        else:
            print form.errors
    else:
        form = ServiceForm(instance=service)
        # form.fields['ip'].queryset=IPAddr.objects.filter(net__segment__pk=service.segment.pk,service=None)
        if not new:
            form.fields['plan'].queryset=Plan.objects.filter(tos__pk=service.plan.tos.pk)
            form.fields['ip'].queryset=IPAddr.objects.filter(net__segment__pk=service.segment.pk).filter(Q(service=None))|IPAddr.objects.filter(service__pk=service.pk)
        else:
            form.fields['plan'].queryset=Plan.objects.none()
            form.fields['ip'].queryset=IPAddr.objects.none()

    return render_to_response('abonent/srv_edit.html', {
                                'form': form,
                                'message': message,
                                'new': new,
                                'abonent' : abonent,
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), },
                                context_instance = RequestContext(request)
                                ) 

@login_required	
def abonent_services(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None

    return render_to_response('abonent/services.html', { 
                                'abonent' : abonent, 
                                'services' : Service.objects.filter(abon__pk=abonent_id), 
                                's_types' : TypeOfService.objects.all(),
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() 
                                }, 
                                context_instance = RequestContext(request))

@login_required    
def abonent_history(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
    ascs = AbonentStatusChanges.objects.filter(abonent__pk=abonent_id).order_by('-pk')
    return render_to_response('abonent/history.html', { 'abonent' : abonent,  'ascs' : ascs, 'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() }, context_instance = RequestContext(request))

@login_required
def abonent_manage(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None

    if request.method == 'POST':
        form = ManageForm(request.POST,instance=abonent)
        if form.is_valid():
            form.save()
    else:
        form = ManageForm(instance=abonent)

    return render_to_response('abonent/manage.html', { 
                                'abonent' : abonent, 
                                'form': form, 
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() },
                              context_instance = RequestContext(request))

@login_required    
def abonent_info(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
        info = None
        template = 'deadend.html'
    else:
        if abonent.utype == 'F':
            info, created = Passport.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'series':'', 'number' : '', 'issued_by' : '', 'date' : datetime.datetime.now(), 'address' : '' })
            if request.method == 'POST':
                form = PassportForm(request.POST,instance=info)
                if form.is_valid():
                    form.save()
            else:
                form = PassportForm(instance=info)
            template = 'abonent/info_person.html'
        else:
            info, created = Detail.objects.get_or_create(abonent__pk=abonent.pk, defaults={'abonent':abonent, 'title':'', 'inn' : '', 'kpp' : '', 'account' : '', 'post_address' : '', 'official_address' : '' })
            # for item in Detail.objects.filter(abonent__pk=abonent.pk):
            #     print item.pk
            if request.method == 'POST':
                form = DetailForm(request.POST,instance=info)
                if form.is_valid():
                    form.save()
                else:
                    print form.errors
            else:
                form = DetailForm(instance=info)
            template = 'abonent/info_company.html'
    return render_to_response(template, { 'abonent' : abonent, 'form': form, 'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() }, context_instance = RequestContext(request))

@login_required
def abonent_tts(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        return render_to_response('deadend.html', { 
                                          'message' : u'Абонент не найден', 
                                    'previous_page' : request.META['HTTP_REFERER'] }  , 
                                    context_instance = RequestContext(request))
    
    tts = TroubleTicket.objects.filter(abonent__pk=abonent_id).order_by('-create_date')    
    return render_to_response('abonent/tts.html', { 
                                                    'abonent' : abonent, 
                                                        'tts' : tts, 
                                                 'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() }, 
                              context_instance = RequestContext(request))

def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if form.get_user():
                login(request, form.get_user())
                return HttpResponseRedirect('/')
    else:
        form = LoginForm()
    return render(request, 'auth.html', {'form': form})

def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')