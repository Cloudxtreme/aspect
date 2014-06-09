# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Note'
        db.create_table(u'notes_note', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('marks', self.gf('django.db.models.fields.CharField')(max_length=13)),
        ))
        db.send_create_signal(u'notes', ['Note'])


    def backwards(self, orm):
        # Deleting model 'Note'
        db.delete_table(u'notes_note')


    models = {
        u'notes.note': {
            'Meta': {'object_name': 'Note'},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marks': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['notes']