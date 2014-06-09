from django.shortcuts import render_to_response
from django.template import RequestContext
from notes.models import Note

# Create your views here.

def notes_all(request):
    note_list = Note.objects.all()
    return render_to_response('notes.html', { 'note_list': note_list }, context_instance = RequestContext(request))
