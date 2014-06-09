# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WriteOffType'
        db.create_table(u'pays_writeofftype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'pays', ['WriteOffType'])

        # Adding model 'WriteOff'
        db.create_table(u'pays_writeoff', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abonent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Abonent'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Service'], null=True, blank=True)),
            ('wot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pays.WriteOffType'])),
            ('summ', self.gf('django.db.models.fields.FloatField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'pays', ['WriteOff'])


    def backwards(self, orm):
        # Deleting model 'WriteOffType'
        db.delete_table(u'pays_writeofftype')

        # Deleting model 'WriteOff'
        db.delete_table(u'pays_writeoff')


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
        u'pays.payment': {
            'Meta': {'object_name': 'Payment'},
            'abon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'sum': ('django.db.models.fields.FloatField', [], {}),
            'top': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pays.PaymentSystem']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'pays.paymentsystem': {
            'Meta': {'object_name': 'PaymentSystem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'pays.writeoff': {
            'Meta': {'object_name': 'WriteOff'},
            'abonent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Abonent']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
            'contact': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.Contact']", 'symmetrical': 'False', 'blank': 'True'}),
            'contract': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_credit': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'reserve': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rest': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'utype': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'users.agent': {
            'Meta': {'object_name': 'Agent'},
            'agent_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'})
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
        u'users.plan': {
            'Meta': {'object_name': 'Plan'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'install_price': ('django.db.models.fields.FloatField', [], {}),
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
            'bs_device': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bs_device'", 'null': 'True', 'to': u"orm['vlans.Device']"}),
            'datefinish': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'datestart': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['vlans.IPAddr']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Node']"}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Plan']"}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Segment']"}),
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

    complete_apps = ['pays']