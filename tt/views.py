# -*- coding: utf-8 -*- 
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from tt.models import TroubleTicket
from tt.forms import TTForm, TTCommentForm
from users.models import Abonent
from datetime import datetime

@login_required
def tt_comment_add(request, abonent_id, tt_id):
    try:
        abonent = Abonent.objects.get(pk = abonent_id)
    except:
        abonent = Abonent()

    tt = TroubleTicket.objects.get(pk=tt_id)

    if request.method == 'POST':
        form = TTCommentForm(request.POST)
        if form.is_valid():
            newttcomment = form.save(commit=False)
            newttcomment.tt = tt
            newttcomment.author = request.user
            newttcomment.save()
            if form.cleaned_data['finished']:
                newttcomment.tt.solve_date = datetime.now()
                newttcomment.tt.save()
            return HttpResponseRedirect(reverse('users.views.abonent_tts', args=[abonent_id]))
    else:
        form = TTCommentForm()

    return render_to_response('abonent/tt_comment_add.html', {
                                'form': form,
                                'tt': tt,
                                'abonent' : abonent},
                                context_instance = RequestContext(request)
                                )          


@login_required
def tt_add(request, abonent_id, tt_id):
    try:
        abonent = Abonent.objects.get(pk = abonent_id)
    except:
        abonent = Abonent()

    if tt_id != '0' :
        message = u'Редактирование обращения'
        new = False
        tt = TroubleTicket.objects.get(pk=tt_id)
    else:
        message = u'Добавление нового обращения'
        new = True
        tt = TroubleTicket()

    if request.method == 'POST':
        form = TTForm(request.POST, instance=tt)
        if form.is_valid():
            newtt = form.save(commit=False)
            newtt.abonent = abonent
            newtt.save()
            return HttpResponseRedirect(reverse('users.views.abonent_tts', args=[abonent_id]))
        else:
            print form.errors
    else:
        form = TTForm(instance=tt)

    return render_to_response('abonent/tt_add.html', {
                                'form': form,
                                'message': message,
                                'new': new,
                                'tt' : tt,
                                'abonent' : abonent},
                                context_instance = RequestContext(request)
                                )  

@login_required
def tt_all(request, performer_id):
    if performer_id == '0':
        tt_list = TroubleTicket.objects.filter(solve_date=None)
    else:
        tt_list = TroubleTicket.objects.filter(solve_date=None,performer__pk=performer_id)
    return render_to_response('tt/tt_list.html', { 'tt_list': tt_list, }, context_instance = RequestContext(request))