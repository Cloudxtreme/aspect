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
from users.forms import  ServiceForm, SearchForm, LoginForm, PassportForm, DetailForm, ManageForm, AbonentForm
from journaling.forms import ServiceStatusChangesForm
from notice.forms import AbonentFilterForm
from users.models import Abonent, Service, TypeOfService, Plan, Passport, Detail
from tt.models import TroubleTicket, TroubleTicketComment
from journaling.models import ServiceStatusChanges, AbonentStatusChanges
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from vlans.models import Network, IPAddr
from django.db.models import Avg, Max, Min, Sum, Q
import datetime
from django.conf import settings

from pays.models import Payment

# @login_required
# def contact(request):
#     if request.method == 'POST': # If the form has been submitted...
#         form = ContactForm(request.POST) # A form bound to the POST data
#         if form.is_valid(): # All validation rules pass
#             # Process the data in form.cleaned_data
#             # ...
#             return HttpResponseRedirect('#') # Redirect after POST
#     else:
#         form = AbonentForm() # An unbound form

#     return render_to_response('fizik.html', {
#         'form': form,
#     }, context_instance = RequestContext(request))

# @login_required	
# def aquicksearch(request):
#     if request.method == 'POST': # If the form has been submitted...
#         data = request.POST
#         abonents = Abonent.objects.filter(contract__icontains=data['q'])|Abonent.objects.filter(title__icontains=data['q'])
#         if abonents.count() == 1:
#             return redirect('abonent_info', abonent_id = abonents[0].pk) 
#         elif abonents.count() == 0:
#             return render_to_response('deadend.html', { 'message' : u'Абоненты не найдены', 'previous_page' : request.META['HTTP_REFERER'] }  , context_instance = RequestContext(request))
#         else:
#             return render_to_response('aqsearch_result.html', { 'abonents' : abonents } , context_instance = RequestContext(request))
#     #return redirect(request.META['HTTP_REFERER'])        

@login_required 
def aquicksearch(request):
    data = request.GET
    abonent_list = Abonent.objects.filter(contract__icontains=data['q'])|Abonent.objects.filter(title__icontains=data['q'])
    paginator = Paginator(abonent_list, 10)

    page = request.GET.get('page')
    try:
        abonents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        abonents = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        abonents = paginator.page(paginator.num_pages)

    if abonent_list.count() == 1:
        return redirect('abonent_info', abonent_id = abonent_list[0].pk) 
    elif abonent_list.count() == 0:
        return render_to_response('deadend.html', { 'message' : u'Абоненты не найдены', 'previous_page' : request.META['HTTP_REFERER'] }  , context_instance = RequestContext(request))
    else:
        return render_to_response('aqsearch_result.html', { 'abonents' : abonents, 'abonent_list_count' : len(abonent_list), 'previous_request' : data['q'] } , context_instance = RequestContext(request))            
        #     return render_to_response('aqsearch_result.html', { 'abonents' : abonents } , context_instance = RequestContext(request))
        
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
        # data = IPAddr.objects.filter(net__segment__pk=request.GET['id'])
        data = IPAddr.objects.filter(net__segment__pk=request.GET['id']).filter(net__net_type='UN').filter(Q(service=None))|IPAddr.objects.filter(service__pk=request.GET['id'])
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
def abonent_add(request,abonent_id=0):
    if abonent_id != '0' :
        message = u'Изменение параметров абонента [%s]' % (abonent_id)
        new = False
        try:
            abonent = Abonent.objects.get(pk = abonent_id)
        except:
            abonent = Abonent()
    else:
        message = u'Добавление нового абонента'
        new = True
        abonent = Abonent()

    if request.method == 'POST':
        form = AbonentForm(request.POST, instance=abonent)
        if form.is_valid():
            newabonent = form.save()
            # form.save(commit=False)
            # service.abon=abonent
            # service.save()
            return HttpResponseRedirect(reverse('abonent_info', args=[newabonent.pk]))
        else:
            print form.errors
    else:
        form = AbonentForm(instance=abonent)
        # form.fields['ip'].queryset=IPAddr.objects.filter(net__segment__pk=service.segment.pk,service=None)
        # if not new:
        #     form.fields['plan'].queryset=Plan.objects.filter(tos__pk=service.plan.tos.pk)
        #     form.fields['ip'].queryset=IPAddr.objects.filter(net__segment__pk=service.segment.pk).filter(Q(service=None))|IPAddr.objects.filter(service__pk=service.pk)
        # else:
        #     form.fields['plan'].queryset=Plan.objects.none()
        #     form.fields['ip'].queryset=IPAddr.objects.none()

    return render_to_response('abonent/add.html', {
                                'form': form,
                                'message': message,
                                'new': new,
                                'abonent' : abonent},
                                context_instance = RequestContext(request)
                                )  

@login_required
def abonent_search(request):
    abonent_list = []
    if request.method == 'POST': # If the form has been submitted...
        form = AbonentFilterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            status = form.cleaned_data['status']
            utype = form.cleaned_data['utype']
            is_credit=form.cleaned_data['is_credit']
            balance_lt=form.cleaned_data['balance_lt']
            balance_gt=form.cleaned_data['balance_gt']
            request.session['status'] = status
            request.session['utype'] = utype
            request.session['is_credit'] = is_credit
            request.session['balance_lt'] = balance_lt
            request.session['balance_gt'] = balance_gt
            abonent_list = Abonent.obj.filter_list(status=status,utype=utype,is_credit=is_credit,balance_lt=balance_lt,balance_gt=balance_gt)
    else:
        form = AbonentFilterForm()

    if request.GET.get('page'):
        abonent_list = Abonent.obj.filter_list(status=request.session['status'],
                                           utype=request.session['utype'],
                                           is_credit=request.session['is_credit'],
                                           balance_lt=request.session['balance_lt'],
                                           balance_gt=request.session['balance_gt'])
    paginator = Paginator(abonent_list, 10)

    page = request.GET.get('page')
    try:
        abonents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        abonents = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        abonents = paginator.page(paginator.num_pages)

    return render_to_response('asearch.html', {'form': form, 'abonents' : abonents, 'abonent_list_count' : len(abonent_list) }, context_instance = RequestContext(request) )

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
    return render_to_response('service/service_edit.html', {
                                'abonent' : abonent, 
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), 
                                'form': form }, 
                                context_instance = RequestContext(request) )    

@login_required
def service_status_change(request, abonent_id, service_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
        service = Service.objects.get(pk=service_id)
    except:
        abonent, service = None 

    if request.method == 'POST':
        form = ServiceStatusChangesForm(request.POST)
        if form.is_valid(): 
            ssc = form.save(commit=False)
            ssc.service = Service.objects.get(pk=service_id)
            ssc.laststatus = Service.objects.get(pk=service_id).status
            ssc.save()
            return HttpResponseRedirect(reverse('services_history', args=[abonent_id, service_id]))
        else:
            print form.errors
    else:
        form = ServiceStatusChangesForm() 
        # form.fields['plan'].queryset=Plan.objects.filter(tos__pk=tos_id)

    return render_to_response('service/service_status_changes.html', {
                                'abonent' : abonent, 
                                'service' : service, 
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
            form.fields['ip'].queryset=IPAddr.objects.filter(net__segment__pk=service.segment.pk).filter(net__net_type='UN').filter(Q(service=None))|IPAddr.objects.filter(service__pk=service.pk)
        else:
            form.fields['plan'].queryset=Plan.objects.none()
            form.fields['ip'].queryset=IPAddr.objects.none()

    return render_to_response('service/service_edit.html', {
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

    return render_to_response('service/services.html', { 
                                'abonent' : abonent, 
                                'services' : Service.objects.filter(abon__pk=abonent_id), 
                                's_types' : TypeOfService.objects.all(),
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() 
                                }, 
                                context_instance = RequestContext(request))

@login_required   
def ssc_delete(request, abonent_id, service_id, ssc_id):
    ServiceStatusChanges.objects.get(pk=ssc_id).delete()
    return HttpResponseRedirect(reverse('services_history', args=[abonent_id, service_id]))

@login_required    
def service_history(request, abonent_id, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
        service = None
    sscs = ServiceStatusChanges.objects.filter(service__pk=service_id).order_by('-pk')
    return render_to_response('service/history.html', { 'abonent' : abonent, 'service' : service,  'sscs' : sscs, 'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count() }, context_instance = RequestContext(request))

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
        form = PassportForm()
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
                # print request.GET.get('next')
                url = settings.LOGIN_REDIRECT_URL if not request.GET.get('next') else request.GET.get('next')
                return HttpResponseRedirect(url)
    else:
        form = LoginForm()
    return render(request, 'auth.html', {'form': form})

def log_out(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)