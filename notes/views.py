# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from notes.models import Note
from notes.forms import NoteModelForm

@login_required
def note_del(request, note_id):
	Note.objects.filter(pk=note_id).delete()
	return HttpResponseRedirect(reverse('notes_all'))

@login_required
def note_read(request, note_id):
    Note.objects.filter(pk=note_id).update(read=True)
    return HttpResponseRedirect(reverse('notes_all'))

@login_required
def note_add(request):
    if request.method == 'POST':
        form = NoteModelForm(request.POST)
        if form.is_valid(): 
            newnote = form.save(commit=False)
            newnote.author = request.user
            newnote.save()
            return HttpResponseRedirect(reverse('notes_all'))
    else:
        form = NoteModelForm()
        header = 'Создать заметку'

    return render_to_response('generic/generic_edit.html', {
                                'header' : header,
                                'form': form,},
                                context_instance = RequestContext(request)
                                ) 

@login_required
def notes_all(request):
    note_list = Note.objects.filter(author=request.user,kind='G').order_by('-pk')|Note.objects.filter(public=True,kind='G').order_by('-date')
    form = NoteModelForm()
    header = 'Список заметок'
    return render_to_response('notes/notes.html', { 'note_list': note_list, 'form' : form, 'header' : header }, context_instance = RequestContext(request))

@login_required
def show_changelog(request):
    note_list = Note.objects.filter(kind='C').order_by('-pk')
    header = 'История изменений'
    return render_to_response('notes/notes.html', { 'note_list': note_list, 'header': header }, context_instance = RequestContext(request))