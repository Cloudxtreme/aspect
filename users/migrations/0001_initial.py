# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Segment'
        db.create_table(u'users_segment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'users', ['Segment'])

        # Adding model 'TypeOfService'
        db.create_table(u'users_typeofservice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'users', ['TypeOfService'])

        # Adding model 'Plan'
        db.create_table(u'users_plan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tos', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.TypeOfService'])),
            ('speed_in', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('speed_out', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('install_price', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'users', ['Plan'])

        # Adding M2M table for field segment on 'Plan'
        m2m_table_name = db.shorten_name(u'users_plan_segment')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('plan', models.ForeignKey(orm[u'users.plan'], null=False)),
            ('segment', models.ForeignKey(orm[u'users.segment'], null=False))
        ))
        db.create_unique(m2m_table_name, ['plan_id', 'segment_id'])

        # Adding model 'Contact'
        db.create_table(u'users_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('second_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'users', ['Contact'])

        # Adding model 'Agent'
        db.create_table(u'users_agent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('agent_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'users', ['Agent'])

        # Adding model 'Abonent'
        db.create_table(u'users_abonent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('contract', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='W', max_length=1)),
            ('utype', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('is_credit', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Agent'], null=True, blank=True)),
            ('balance', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('reserve', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('rest', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'users', ['Abonent'])

        # Adding M2M table for field contact on 'Abonent'
        m2m_table_name = db.shorten_name(u'users_abonent_contact')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('abonent', models.ForeignKey(orm[u'users.abonent'], null=False)),
            ('contact', models.ForeignKey(orm[u'users.contact'], null=False))
        ))
        db.create_unique(m2m_table_name, ['abonent_id', 'contact_id'])

        # Adding model 'Bank'
        db.create_table(u'users_bank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('bik', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('account', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'users', ['Bank'])

        # Adding model 'Passport'
        db.create_table(u'users_passport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('issued_by', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('abonent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Abonent'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'users', ['Passport'])

        # Adding model 'Detail'
        db.create_table(u'users_detail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('inn', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('kpp', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('account', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('post_address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('official_address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('bank', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Bank'], null=True, blank=True)),
            ('abonent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Abonent'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'users', ['Detail'])

        # Adding model 'Service'
        db.create_table(u'users_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Abonent'])),
            ('tos', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.TypeOfService'])),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Segment'])),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Plan'])),
            ('ip', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['vlans.IPAddr'], unique=True, null=True, blank=True)),
            ('adm_status', self.gf('django.db.models.fields.CharField')(default='W', max_length=1)),
            ('speed_in', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('speed_out', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlans.Node'])),
            ('datestart', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 5, 27, 0, 0))),
            ('datefinish', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('user_device', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='user_device', null=True, to=orm['vlans.Device'])),
            ('bs_device', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='bs_device', null=True, to=orm['vlans.Device'])),
        ))
        db.send_create_signal(u'users', ['Service'])


    def backwards(self, orm):
        # Deleting model 'Segment'
        db.delete_table(u'users_segment')

        # Deleting model 'TypeOfService'
        db.delete_table(u'users_typeofservice')

        # Deleting model 'Plan'
        db.delete_table(u'users_plan')

        # Removing M2M table for field segment on 'Plan'
        db.delete_table(db.shorten_name(u'users_plan_segment'))

        # Deleting model 'Contact'
        db.delete_table(u'users_contact')

        # Deleting model 'Agent'
        db.delete_table(u'users_agent')

        # Deleting model 'Abonent'
        db.delete_table(u'users_abonent')

        # Removing M2M table for field contact on 'Abonent'
        db.delete_table(db.shorten_name(u'users_abonent_contact'))

        # Deleting model 'Bank'
        db.delete_table(u'users_bank')

        # Deleting model 'Passport'
        db.delete_table(u'users_passport')

        # Deleting model 'Detail'
        db.delete_table(u'users_detail')

        # Deleting model 'Service'
        db.delete_table(u'users_service')


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
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vlans.Node']"}),
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