from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from notes.models import Note
from notes.forms import NoteModelForm

# Create your views here.
def note_del(request, note_id):
	Note.objects.get(pk=note_id).delete()
	return HttpResponseRedirect(reverse('notes_all'))

def note_add(request):
	if request.method == 'POST':
		form = NoteModelForm(request.POST)
        if form.is_valid(): 
            newnote = form.save(commit=False)
            newnote.save()
        else:
            print form.errors
	return HttpResponseRedirect(reverse('notes_all'))

def notes_all(request):
    note_list = Note.objects.all().order_by('-pk')
    form = NoteModelForm()
    return render_to_response('notes.html', { 'note_list': note_list, 'form' : form }, context_instance = RequestContext(request))
