# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WriteOff.newbalance'
        db.add_column(u'pays_writeoff', 'newbalance',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'WriteOff.newbalance'
        db.delete_column(u'pays_writeoff', 'newbalance')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'devices.device': {
            'Meta': {'object_name': 'Device'},
            'comment': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'devtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.DevType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interfaces': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['users.Interface']", 'null': 'True', 'blank': 'True'}),
            'inv_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'last_available': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Location']", 'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mgmt_vlan': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mgmt_vlan'", 'null': 'True', 'to': u"orm['vlans.Vlan']"}),
            'router': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'devices.devtype': {
            'Meta': {'object_name': 'DevType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ports': ('django.db.models.fields.IntegerField', [], {}),
            'supply': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'pays.payment': {
            'Meta': {'object_name': 'Payment'},
            'abonent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'abonent'", 'to': u"orm['users.Abonent']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newbalance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'num': ('django.db.models.fields.CharField', [], {'default': "u'002123'", 'unique': 'True', 'max_length': '30'}),
            'summ': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'top': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pays.PaymentSystem']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'pays.paymentsystem': {
            'Meta': {'object_name': 'PaymentSystem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stat': ('django.db.models.fields.BooleanField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'pays.promisedpays': {
            'Meta': {'object_name': 'PromisedPays'},
            'abonent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'datefinish': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'datestart': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pay_onaccount': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repaid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'summ': ('django.db.models.fields.FloatField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'pays.writeoff': {
            'Meta': {'object_name': 'WriteOff'},
            'abonent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newbalance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'number': ('django.db.models.fields.CharField', [], {'default': 'None', 'unique': 'True', 'max_length': '20'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Service']", 'null': 'True', 'blank': 'True'}),
            'summ': ('django.db.models.fields.FloatField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pays.WriteOffType']"})
        },
        u'pays.writeofftype': {
            'Meta': {'object_name': 'WriteOffType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
        u'users.interface': {
            'Meta': {'ordering': "['ip']", 'object_name': 'Interface'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'for_device': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['vlans.IPAddr']", 'unique': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '17', 'null': 'True', 'blank': 'True'})
        },
        u'users.pipe': {
            'Meta': {'ordering': "['speed_in', 'speed_out']", 'object_name': 'Pipe'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'speed_in': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'speed_out': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'users.plan': {
            'Meta': {'object_name': 'Plan'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'install_price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'segment': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.Segment']", 'symmetrical': 'False'}),
            'speed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Pipe']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tos': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.TypeOfService']"}),
            'utype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
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
            'adm_status': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'bs_device': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bs_device'", 'null': 'True', 'to': u"orm['devices.Device']"}),
            'datefinish': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'datestart': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2015, 1, 19, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ifaces': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['users.Interface']", 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Location']", 'null': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Plan']"}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Segment']"}),
            'speed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Pipe']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'tos': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.TypeOfService']"}),
            'user_device': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_device'", 'null': 'True', 'to': u"orm['devices.Device']"}),
            'vlan_list': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'vlan_list'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['vlans.Vlan']"})
        },
        u'users.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'users.typeofservice': {
            'Meta': {'object_name': 'TypeOfService'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'vlans.ipaddr': {
            'Meta': {'ordering': "['decip']", 'object_name': 'IPAddr'},
            'decip': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'net': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Network']"})
        },
        u'vlans.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bs_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'geolocation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'vlans.network': {
            'Meta': {'ordering': "['decip']", 'unique_together': "(('ip', 'mask'),)", 'object_name': 'Network'},
            'decip': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_dhcpd': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'mask': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'net_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['vlans.Network']"}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Segment']"}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Vlan']", 'null': 'True', 'blank': 'True'})
        },
        u'vlans.vlan': {
            'Meta': {'ordering': "['number']", 'object_name': 'Vlan'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['pays']