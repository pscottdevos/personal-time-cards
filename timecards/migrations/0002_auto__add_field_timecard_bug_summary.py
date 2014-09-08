# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TimeCard.bug_summary'
        db.add_column(u'timecards_timecard', 'bug_summary',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TimeCard.bug_summary'
        db.delete_column(u'timecards_timecard', 'bug_summary')


    models = {
        u'timecards.timecard': {
            'Meta': {'object_name': 'TimeCard'},
            'bug': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'bug_summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['timecards']
