# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Vlan'
        db.create_table(u'vlans_vlan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'vlans', ['Vlan'])

        # Adding model 'Node'
        db.create_table(u'vlans_node', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('latlng', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('bs_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal(u'vlans', ['Node'])

        # Adding model 'DevType'
        db.create_table(u'vlans_devtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vendor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('supply', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('ports', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'vlans', ['DevType'])

        # Adding model 'Network'
        db.create_table(u'vlans_network', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['vlans.Network'])),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('mask', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.Vlan'], null=True, blank=True)),
            ('net_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('decip', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Segment'])),
        ))
        db.send_create_signal(u'vlans', ['Network'])

        # Adding unique constraint on 'Network', fields ['ip', 'mask']
        db.create_unique(u'vlans_network', ['ip', 'mask'])

        # Adding model 'IPAddr'
        db.create_table(u'vlans_ipaddr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15)),
            ('net', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.Network'])),
            ('decip', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'vlans', ['IPAddr'])

        # Adding model 'Device'
        db.create_table(u'vlans_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('ip', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['vlans.IPAddr'], unique=True, null=True, blank=True)),
            ('mgmt_vlan', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mgmt_vlan', null=True, to=orm['vlans.Vlan'])),
            ('devtype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.DevType'])),
            ('is_rooter', self.gf('django.db.models.fields.BooleanField')()),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.Node'])),
            ('check_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('snmp_community', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('last_available', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'vlans', ['Device'])


    def backwards(self, orm):
        # Removing unique constraint on 'Network', fields ['ip', 'mask']
        db.delete_unique(u'vlans_network', ['ip', 'mask'])

        # Deleting model 'Vlan'
        db.delete_table(u'vlans_vlan')

        # Deleting model 'Node'
        db.delete_table(u'vlans_node')

        # Deleting model 'DevType'
        db.delete_table(u'vlans_devtype')

        # Deleting model 'Network'
        db.delete_table(u'vlans_network')

        # Deleting model 'IPAddr'
        db.delete_table(u'vlans_ipaddr')

        # Deleting model 'Device'
        db.delete_table(u'vlans_device')


    models = {
        u'users.segment': {
            'Meta': {'object_name': 'Segment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'vlans.device': {
            'Meta': {'object_name': 'Device'},
            'check_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'devtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.DevType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['vlans.IPAddr']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'is_rooter': ('django.db.models.fields.BooleanField', [], {}),
            'last_available': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mgmt_vlan': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mgmt_vlan'", 'null': 'True', 'to': u"orm['vlans.Vlan']"}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Node']"}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'snmp_community': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'vlans.devtype': {
            'Meta': {'object_name': 'DevType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ports': ('django.db.models.fields.IntegerField', [], {}),
            'supply': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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