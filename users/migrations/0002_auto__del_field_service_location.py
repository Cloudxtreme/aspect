# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Service.location'
        db.delete_column(u'users_service', 'location_id')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Service.location'
        raise RuntimeError("Cannot reverse this migration. 'Service.location' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Service.location'
        db.add_column(u'users_service', 'location',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.Node']),
                      keep_default=False)


    models = {
        u'users.abonent': {
            'Meta': {'object_name': 'Abonent'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Agent']", 'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'contact': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.Contact']", 'symmetrical': 'False', 'blank': 'True'}),
            'contract': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_credit': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'reserve': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rest': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'utype': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'users.agent': {
            'Meta': {'object_name': 'Agent'},
            'agent_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        u'users.bank': {
            'Meta': {'object_name': 'Bank'},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bik': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'users.contact': {
            'Meta': {'object_name': 'Contact'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'second_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'users.detail': {
            'Meta': {'object_name': 'Detail'},
            'abonent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'account': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Bank']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inn': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'kpp': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'official_address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'post_address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'users.passport': {
            'Meta': {'object_name': 'Passport'},
            'abonent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued_by': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        u'users.plan': {
            'Meta': {'object_name': 'Plan'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'install_price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'segment': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.Segment']", 'symmetrical': 'False'}),
            'speed_in': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'speed_out': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tos': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.TypeOfService']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'users.segment': {
            'Meta': {'object_name': 'Segment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'users.service': {
            'Meta': {'object_name': 'Service'},
            'abon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']"}),
            'adm_status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'bs_device': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bs_device'", 'null': 'True', 'to': u"orm['vlans.Device']"}),
            'datefinish': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'datestart': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 5, 27, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['vlans.IPAddr']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Plan']"}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Segment']"}),
            'speed_in': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'speed_out': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'tos': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.TypeOfService']"}),
            'user_device': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_device'", 'null': 'True', 'to': u"orm['vlans.Device']"})
        },
        u'users.typeofservice': {
            'Meta': {'object_name': 'TypeOfService'},
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

    complete_apps = ['users']