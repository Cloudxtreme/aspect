# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'GroupEmailMessage'
        db.delete_table(u'notice_groupemailmessage')

        # Removing M2M table for field abonent_list on 'GroupEmailMessage'
        db.delete_table(db.shorten_name(u'notice_groupemailmessage_abonent_list'))

        # Deleting field 'EmailMessage.group_id'
        db.delete_column(u'notice_emailmessage', 'group_id')


    def backwards(self, orm):
        # Adding model 'GroupEmailMessage'
        db.create_table(u'notice_groupemailmessage', (
            ('content', self.gf('tinymce.models.HTMLField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=70)),
        ))
        db.send_create_signal(u'notice', ['GroupEmailMessage'])

        # Adding M2M table for field abonent_list on 'GroupEmailMessage'
        m2m_table_name = db.shorten_name(u'notice_groupemailmessage_abonent_list')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupemailmessage', models.ForeignKey(orm[u'notice.groupemailmessage'], null=False)),
            ('abonent', models.ForeignKey(orm[u'users.abonent'], null=False))
        ))
        db.create_unique(m2m_table_name, ['groupemailmessage_id', 'abonent_id'])

        # Adding field 'EmailMessage.group_id'
        db.add_column(u'notice_emailmessage', 'group_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True),
                      keep_default=False)


    models = {
        u'notice.abonentevent': {
            'Meta': {'object_name': 'AbonentEvent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['notice.TemplateMessage']", 'null': 'True', 'blank': 'True'}),
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