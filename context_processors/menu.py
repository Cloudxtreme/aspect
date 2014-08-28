from django.core.context_processors import request
from tt.models import TroubleTicket
from notes.models import Note
 
def menu(request):
    return { "open_tt" : TroubleTicket.objects.filter(solve_date=None).count, 'my_tt' : TroubleTicket.objects.filter(solve_date=None,performer__pk=request.user.pk).count, 'notes_count' : Note.objects.filter(author=request.user).count() }