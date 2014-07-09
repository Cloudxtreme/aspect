# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailMessage'
        db.create_table(u'notice_emailmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'notice', ['EmailMessage'])


    def backwards(self, orm):
        # Deleting model 'EmailMessage'
        db.delete_table(u'notice_emailmessage')


    models = {
        u'notice.emailmessage': {
            'Meta': {'object_name': 'EmailMessage'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        }
    }

    complete_apps = ['notice']