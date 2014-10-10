# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TemplateMessage.subject'
        db.add_column(u'notice_templatemessage', 'subject',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TemplateMessage.subject'
        db.delete_column(u'notice_templatemessage', 'subject')


    models = {
        u'notice.abonentevent': {
            'Meta': {'object_name': 'AbonentEvent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template_fiz': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'template_fiz'", 'null': 'True', 'to': u"orm['notice.TemplateMessage']"}),
            'template_ur': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'template_ur'", 'null': 'True', 'to': u"orm['notice.TemplateMessage']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'notice.emailmessage': {
            'Meta': {'object_name': 'EmailMessage'},
            'abonent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']", 'null': 'True', 'blank': 'True'}),
            'content': ('tinymce.models.HTMLField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        u'notice.templatemessage': {
            'Meta': {'object_name': 'TemplateMessage'},
            'content': ('tinymce.models.HTMLField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'users.abonent': {
            'Meta': {'object_name': 'Abonent'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Agent']", 'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'contract': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_credit': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'notice_email': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'notice_mobile': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True', 'blank': 'True'}),
            'reserve': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rest': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'tag': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['users.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'utype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'vip': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'users.agent': {
            'Meta': {'object_name': 'Agent'},
            'agent_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        u'users.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        }
    }

    complete_apps = ['notice']