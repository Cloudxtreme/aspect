# -*- coding: utf-8 -*- 
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from notice.models import EmailMessage
from notice.forms import MassNoticeForm
from users.models import Abonent, Service
from datetime import datetime

@login_required
def notice_email_del(request,  abonent_id, notice_id):
    EmailMessage.objects.get(pk=notice_id).delete()
    return HttpResponseRedirect(reverse('for_abonent', args=[abonent_id]))

@login_required
def mass_notice_add(request):
    if request.method == 'POST':
        form = MassNoticeForm(request.POST)
        # if form.is_valid():
        #     newttcomment = form.save(commit=False)
        #     newttcomment.tt = tt
        #     newttcomment.author = request.user
        #     newttcomment.save()
        #     if form.cleaned_data['finished']:
        #         newttcomment.tt.solve_date = datetime.now()
        #         newttcomment.tt.save()
        #     return HttpResponseRedirect(reverse('users.views.abonent_tts', args=[abonent_id]))
    else:
        form = MassNoticeForm()

    return render_to_response('mass_notice_add.html', {
                                'form': form,},
                                context_instance = RequestContext(request)
                                )          

@login_required
def for_abonent(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None

    notice_list = EmailMessage.objects.filter(abonent__pk=abonent_id).order_by('-pk')
    return render_to_response('abonent/notice_all.html', { 
                                'notice_list': notice_list, 
                                'abonent' : abonent,
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), 
                                }, context_instance = RequestContext(request))