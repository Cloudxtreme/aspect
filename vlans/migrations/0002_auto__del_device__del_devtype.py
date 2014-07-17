# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Device'
        db.delete_table(u'vlans_device')

        # Deleting model 'DevType'
        db.delete_table(u'vlans_devtype')


    def backwards(self, orm):
        # Adding model 'Device'
        db.create_table(u'vlans_device', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.Node'])),
            ('snmp_community', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('check_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('ip', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['vlans.IPAddr'], unique=True, null=True, blank=True)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('is_rooter', self.gf('django.db.models.fields.BooleanField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_available', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('mgmt_vlan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mgmt_vlan', null=True, to=orm['vlans.Vlan'], blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('devtype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.DevType'])),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal(u'vlans', ['Device'])

        # Adding model 'DevType'
        db.create_table(u'vlans_devtype', (
            ('vendor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('supply', self.gf('django.db.models.fields.CharField')(max_length=4)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ports', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'vlans', ['DevType'])


    models = {
        u'users.segment': {
            'Meta': {'object_name': 'Segment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'vlans.ipaddr': {
            'Meta': {'ordering': "['decip']", 'object_name': 'IPAddr'},
            'decip': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'net': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Network']"})
        },
        u'vlans.network': {
            'Meta': {'ordering': "['decip']", 'unique_together': "(('ip', 'mask'),)", 'object_name': 'Network'},
            'decip': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'mask': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'net_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['vlans.Network']"}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Segment']"}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Vlan']", 'null': 'True', 'blank': 'True'})
        },
        u'vlans.node': {
            'Meta': {'object_name': 'Node'},
            'bs_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlng': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'vlans.vlan': {
            'Meta': {'object_name': 'Vlan'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['vlans']