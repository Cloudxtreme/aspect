from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from tt.models import TroubleTicket

# Create your views here.
# @login_required
# def note_del(request, note_id):
# 	Note.objects.get(pk=note_id).delete()
# 	return HttpResponseRedirect(reverse('notes_all'))

# @login_required
# def note_add(request):
# 	if request.method == 'POST':
# 		form = NoteModelForm(request.POST)
#         if form.is_valid(): 
#             newnote = form.save(commit=False)
#             newnote.save()
#         else:
#             print form.errors
# 	return HttpResponseRedirect(reverse('notes_all'))

@login_required
def tt_all(request):
    tt_list = TroubleTicket.objects.filter(solve_date=None)
    return render_to_response('tt/tt_list.html', { 'tt_list': tt_list, }, context_instance = RequestContext(request))