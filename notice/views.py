# -*- coding: utf-8 -*- 
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from notice.models import EmailMessage
from notice.forms import AbonentFilterForm, GroupEmailForm
from users.models import Abonent, Service
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from django.db.models import Max

@login_required
def notice_email_del(request,  abonent_id, notice_id):
    EmailMessage.objects.get(pk=notice_id).delete()
    if abonent_id == '0':
        return HttpResponseRedirect(reverse('email_all', args=[0]))
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
                                          group_id=1 + (EmailMessage.objects.all().aggregate(Max('group_id'))['group_id__max'] or 0) )]
            EmailMessage.objects.bulk_create(eList)
            return HttpResponseRedirect(reverse('email_group',))
    else:
        form = GroupEmailForm()
    
    return render_to_response('write_groupemail.html', {
                                'form': form, 
                                }, context_instance = RequestContext(request))     

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
            # abonent_list = Abonent.objects.all()
            # if status:
            #     abonent_list = abonent_list.filter(status__in=status)
            # if utype:
            #     abonent_list = abonent_list.filter(utype__in=utype)
            # if is_credit:
            #     abonent_list = abonent_list.filter(is_credit__in=is_credit)
            # if balance_lt or balance_lt==0:
            #     abonent_list = abonent_list.filter(balance__lte=balance_lt)
            # if balance_gt or balance_gt==0:
            #     abonent_list = abonent_list.filter(balance__gte=balance_gt)
    else:
        abonent_list = [] 
        form = AbonentFilterForm()
        
    return render_to_response('mass_notice_add.html', {
                                'abonent_list' : abonent_list,
                                'form': form, 
                                'messageform' : messageform,
                                }, context_instance = RequestContext(request))  

@login_required
def email_all(request,group_id):
    if group_id == '0': 
        notice_list = EmailMessage.objects.order_by('-pk')
    else: 
        notice_list = EmailMessage.objects.filter(group_id=group_id).order_by('-pk')
    return render_to_response('email_all.html', { 
                                'notice_list': notice_list, 
                                }, context_instance = RequestContext(request))

@login_required
def email_group(request):
    notice_list = EmailMessage.objects.exclude(group_id=0).order_by('-pk')

    return render_to_response('email_all.html', { 
                                'notice_list': notice_list, 
                                }, context_instance = RequestContext(request))

@login_required
def for_abonent(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None

    notice_list = EmailMessage.objects.filter(abonent__pk=abonent_id).order_by('-pk')
    return render_to_response('abonent/for_abonent.html', { 
                                'notice_list': notice_list, 
                                'abonent' : abonent,
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), 
                                }, context_instance = RequestContext(request))