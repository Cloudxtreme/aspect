# -*- coding: utf-8 -*- 
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from notice.models import EmailMessage, AbonentEvent, TemplateMessage, SMSMessage
from notice.forms import AbonentFilterForm, AbonentEventForm, TemplateMessageForm, GroupEmailForm, EmailMessageForm, InvoiceMessageForm,SMSMessageForm
from users.models import Abonent, Service
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from django.db.models import Max
import smsru

@login_required
def create_invoice(request):
    message = ''
    if request.method == 'POST':
        form = InvoiceMessageForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.save(commit=False)
            abonent_event = AbonentEvent.objects.get(pk=5) # Прикреплен файл
            email.subject = abonent_event.template_ur.subject
            email.content = abonent_event.template_ur.content
            email.destination = email.abonent.notice_email
            email.save()
            message  = "Счет создан" 
            form = InvoiceMessageForm()
        else:
            message = "Ошибки в форме"
    else:
        form = InvoiceMessageForm()
    header = 'Отправка счета клиенту'

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'message' : message,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

@login_required
def template_del(request,template_id):
    try:
        TemplateMessage.objects.get(pk = template_id).delete()
    except:
        raise Http404

    return HttpResponseRedirect(reverse('templates_all'))    

@login_required
def abonentevent_del(request,abonentevent_id):
    try:
        AbonentEvent.objects.get(pk = abonentevent_id).delete()
    except:
        raise Http404

    return HttpResponseRedirect(reverse('abonentevents_all'))  

@login_required
def templates_all(request):
    templates_list = TemplateMessage.objects.all().order_by('pk')

    return render_to_response('notice/templates_all.html', { 
                                'templates_list': templates_list, 
                                }, context_instance = RequestContext(request)
                                ) 

@login_required
def abonentevents_all(request):
    abonentevents_list = AbonentEvent.objects.all().order_by('pk')

    return render_to_response('notice/abonentevents_all.html', { 
                                'abonentevents_list': abonentevents_list, 
                                }, context_instance = RequestContext(request)
                                ) 

@login_required
def template_edit(request, template_id):
    try:
        template = TemplateMessage.objects.get(pk = template_id)
        header = 'Редактирование шаблона'    
    except:
        template = TemplateMessage()
        header = 'Создание нового шаблона'    

    if request.method == 'POST':
        form = TemplateMessageForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('templates_all'))
    else:
        form = TemplateMessageForm(instance=template)

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

@login_required
def abonentevent_edit(request, abonentevent_id):
    try:
        abonent_event = AbonentEvent.objects.get(pk = abonentevent_id)
        header = 'Редактирование события'    
    except:
        abonent_event = AbonentEvent()
        header = 'Создание нового события'        

    if request.method == 'POST':
        form = AbonentEventForm(request.POST, instance=abonent_event)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('abonentevents_all'))
    else:
        form = AbonentEventForm(instance=abonent_event)

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

@login_required
def emailmessage_edit(request, emailmessage_id):
    try:
        template = EmailMessage.objects.get(pk = emailmessage_id)
        header = 'Редактирование уведомления'    
    except:
        raise Http404    

    if request.method == 'POST':
        form = EmailMessageForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('email_all'))
    else:
        form = EmailMessageForm(instance=template)

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

@login_required
def notice_email_del(request,  abonent_id, notice_id):
    EmailMessage.objects.filter(pk=notice_id).delete()
    if abonent_id == '0':
        return HttpResponseRedirect(reverse('email_all'))
    else:
        return HttpResponseRedirect(reverse('for_abonent', args=[abonent_id]))

@login_required
def write_groupemail(request):
    if request.method == 'POST':
        abonent_list = request.POST.getlist('abonent_list')
        form = GroupEmailForm(request.POST)
        lst = [(item.pk, item.title) for item in Abonent.objects.filter(pk__in=abonent_list)]
        form.fields['abonent_list'].choices=lst
        if form.is_valid():
            subject = form.cleaned_data['subject']
            content = form.cleaned_data['content']
            date = form.cleaned_data['date']
            eList = []
            for item in abonent_list:
                abonent = Abonent.objects.get(pk=item)
                # здесь подставновка значения поля вместо его имени!
                filtered_content = content
                for field in abonent.__dict__.keys():
                    filtered_content=filtered_content.replace('[%s]' % field, '%s' % abonent.__dict__[field] )

                if  abonent.notice_email:
                    content += ''
                    eList += [EmailMessage(abonent = abonent,
                                          destination = abonent.notice_email,
                                          subject=subject,
                                          content=filtered_content,
                                          date=date,
                             )]
            EmailMessage.objects.bulk_create(eList)
            return HttpResponseRedirect(reverse('email_all',))
    else:
        form = GroupEmailForm()

    return render_to_response('generic/generic_edit.html', { 
                                'header' : 'Групповое сообщение',
                                'form': form,
                                'extend': 'index.html', },
                                 context_instance = RequestContext(request))

@login_required
def mass_notice_add(request):
    abonent_list = [] 
    messageform = GroupEmailForm()
    if request.method == 'POST':
        form = AbonentFilterForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            utype = form.cleaned_data['utype']
            is_credit=form.cleaned_data['is_credit']
            balance_lt=form.cleaned_data['balance_lt']
            balance_gt=form.cleaned_data['balance_gt']
            abonent_list = Abonent.obj.filter_list(status=status,utype=utype,is_credit=is_credit,balance_lt=balance_lt,balance_gt=balance_gt)
    else:
        abonent_list = [] 
        form = AbonentFilterForm()
        
    return render_to_response('mass_notice_add.html', {
                                'abonent_list' : abonent_list,
                                'form': form, 
                                'messageform' : messageform,
                                }, context_instance = RequestContext(request))  

@login_required
def send_message(request,message_id):
    try:
        email = EmailMessage.objects.get(pk=message_id)
    except:
        raise Http404
    else:
        email.sendit()
    return HttpResponseRedirect(reverse('email_all'))

@login_required
def sms_send(request,sms_id):
    try:
        sms = SMSMessage.objects.get(pk=sms_id)
    except:
        raise Http404
    else:
        sms.sendit()
    return HttpResponseRedirect(reverse('sms_all'))

@login_required
def sms_edit(request,sms_id):
    try:
        sms = SMSMessage.objects.get(pk = sms_id)
        header = 'Редактирование SMS-уведомления'    
    except:
        sms = SMSMessage()
        header = 'Создание SMS-уведомления'

    if request.method == 'POST':
        form = SMSMessageForm(request.POST, instance=sms)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('sms_all'))
    else:
        form = SMSMessageForm(instance=sms)

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,
                                'extend': 'index.html',},
                                context_instance = RequestContext(request)
                                ) 

@login_required
def sms_del(request,sms_id):
    try:
        sms = SMSMessage.objects.get(pk=sms_id)
    except:
        raise Http404
    else:
        sms.delete()
    return HttpResponseRedirect(reverse('sms_all'))

@login_required
def notices_exec(request):
    for item in EmailMessage.objects.filter(date__lte=datetime.now(), sent=False):
        item.sendit()

    return HttpResponseRedirect(reverse('email_all'))

@login_required
def sms_all_send(request):
    for item in SMSMessage.objects.filter(date__lte=datetime.now(), sent=False):
        item.sendit()

    return HttpResponseRedirect(reverse('sms_all'))

@login_required
def sms_all(request):
    sms_list = SMSMessage.objects.all()
    count = SMSMessage.objects.filter(sent=False).count()
    cli = smsru.Client()
    balance = cli.balance()

    paginator = Paginator(sms_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        smss = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        smss = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        smss = paginator.page(paginator.num_pages)

    return render(request,'notice/sms_all.html', { 
                                'smss': smss, 
                                'count' : count,
                                'balance' : balance,
                                }, context_instance = RequestContext(request))

@login_required
def email_all(request):
    email_list = EmailMessage.objects.all()
    count = EmailMessage.objects.filter(sent=False).count()

    paginator = Paginator(email_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        emails = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        emails = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        emails = paginator.page(paginator.num_pages)
    
    return render(request, 'notice/email_all.html', { 
                                'emails': emails, 
                                'count' : count,
                                }, context_instance = RequestContext(request))

@login_required
def for_abonent(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    notice_list = EmailMessage.objects.filter(abonent__pk=abonent_id).order_by('-pk')
    return render_to_response('abonent/abonent_notices.html', { 
                                'notice_list': notice_list, 
                                'abonent' : abonent,
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), 
                                }, context_instance = RequestContext(request))

@login_required
def sms_abonent(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        raise Http404

    notice_list = SMSMessage.objects.filter(abonent__pk=abonent_id).order_by('-pk')
    return render_to_response('abonent/sms_notices.html', { 
                                'notice_list': notice_list, 
                                'abonent' : abonent,
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), 
                                }, context_instance = RequestContext(request))
