from django.core.context_processors import request
from tt.models import TroubleTicket
 
def menu(request):
    return { "open_tt" : TroubleTicket.objects.filter(solve_date=None).count }