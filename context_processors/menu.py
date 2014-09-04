from django.core.context_processors import request
from tt.models import TroubleTicket
from notes.models import Note
 
def menu(request):
    if request.user.pk:
        my_tt = TroubleTicket.objects.filter(solve_date=None,performer=request.user).count
        notes_count = Note.objects.filter(author=request.user,read=False).count()
    else:
        my_tt = 0
        notes_count = 0
    return { "open_tt" : TroubleTicket.objects.filter(solve_date=None).count, 
               'my_tt' : my_tt, 
         'notes_count' : notes_count }