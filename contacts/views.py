from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from contacts.models import Contact
from contacts.forms import ContactModelForm

@login_required
def contact_del(request, contact_id):
	Contact.objects.get(pk=contact_id).delete()
	return HttpResponseRedirect(reverse('contacts_all'))

@login_required
def contact_add(request):
	if request.method == 'POST':
		form = ContactModelForm(request.POST)
        if form.is_valid(): 
            newcontact = form.save(commit=False)
            newcontact.save()
        else:
            print form.errors
	return HttpResponseRedirect(reverse('contacts_all'))

@login_required
def contacts_all(request):
    contact_list = contact.objects.all().order_by('-pk')
    form = ContactModelForm()
    return render_to_response('contacts.html', { 'contact_list': contact_list, 'form' : form }, context_instance = RequestContext(request))
