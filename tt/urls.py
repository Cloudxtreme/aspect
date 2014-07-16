from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
#     url(r'^add/$','notes.views.note_add', name='note_add'),
#     url(r'^(?P<note_id>\d+)/del/$','notes.views.note_del', name='note_del'),
    url(r'^all/$', 'tt.views.tt_all', name='tt_all'),
)