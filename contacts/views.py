# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from contacts.models import Contact
from contacts.forms import ContactModelForm
from users.models import Abonent, Service

@login_required
def contact_del(request,  abonent_id, contact_id):
	Contact.objects.get(pk=contact_id).delete()
	return HttpResponseRedirect(reverse('contacts', args=[abonent_id]))

@login_required
def contact_edit(request, abonent_id, contact_id=0):
    if contact_id != '0' :
        message = u'Изменение контактной информации'
        new = False
        contact = Contact.objects.get(pk=contact_id)
    else:
        message = u'Добавление нового контакта'
        new = True
        contact = Contact()

    try:
        abonent = Abonent.objects.get(pk = abonent_id)
    except:
        abonent = None

    if request.method == 'POST':
        form = ContactModelForm(request.POST, instance=contact)
        if form.is_valid():
            form.save(commit=False)
            contact.abonent=abonent
            contact.save()
            return HttpResponseRedirect(reverse('contacts', args=[abonent_id]))
        else:
            print form.errors
    else:
        form = ContactModelForm(instance=contact)

    return render_to_response('contact/contact_edit.html', {
                                'form': form,
                                'message': message,
                                'new': new,
                                'abonent' : abonent,
                                'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(), },
                                context_instance = RequestContext(request)
                                ) 

@login_required
def contacts_all(request, abonent_id):
    try:
        abonent = Abonent.objects.get(pk=abonent_id)
    except:
        abonent = None
    contacts = Contact.objects.filter(abonent__pk=abonent_id)
    form = ContactModelForm()
    return render_to_response('contact/contacts.html', 
                              { 
                              'abonent' : abonent,
                              'contacts': contacts,
                              'count_serv' : Service.objects.filter(abon__pk=abonent_id).exclude(status='D').count(),  
                              'form' : form 
                              }, 
                              context_instance = RequestContext(request))
