from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    # url(r'^add/$','tt.views.tt_add', name='tt_add'),
#     url(r'^(?P<note_id>\d+)/del/$','notes.views.note_del', name='note_del'),
    url(r'^all/performer/(?P<performer_id>\d+)$', 'tt.views.tt_all', name='tt_all'),
)