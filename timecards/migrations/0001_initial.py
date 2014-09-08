# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TimeCard'
        db.create_table(u'timecards_timecard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bug', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('start', self.gf('django.db.models.fields.TimeField')(blank=True)),
            ('end', self.gf('django.db.models.fields.TimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'timecards', ['TimeCard'])


    def backwards(self, orm):
        # Deleting model 'TimeCard'
        db.delete_table(u'timecards_timecard')


    models = {
        u'timecards.timecard': {
            'Meta': {'object_name': 'TimeCard'},
            'bug': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['timecards']
