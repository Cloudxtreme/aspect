from django.core.context_processors import request
from tt.models import TroubleTicket
from notes.models import Note
 
def menu(request):
    if request.user.pk:
        my_tt = TroubleTicket.objects.filter(solve_date=None,performer=request.user).count
        unread_notes_count = Note.objects.filter(author=request.user,read=False,kind='G').count()
        all_notes_count = Note.objects.filter(author=request.user,kind='G').count()
    else:
        my_tt = 0
        all_notes_count = 0
        unread_notes_count = 0
    version = Note.objects.filter(kind='C').order_by('-date')[0].title

    return { "open_tt" : TroubleTicket.objects.filter(solve_date=None).count, 
               'my_tt' : my_tt, 
         'all_notes_count' : all_notes_count,
         'unread_notes_count': unread_notes_count,
         'version':version }