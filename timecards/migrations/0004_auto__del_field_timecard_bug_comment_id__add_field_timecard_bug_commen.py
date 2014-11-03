# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'TimeCard.bug_comment_id'
        db.delete_column(u'timecards_timecard', 'bug_comment_id')

        # Adding field 'TimeCard.bug_comment_added'
        db.add_column(u'timecards_timecard', 'bug_comment_added',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'TimeCard.bug_comment_id'
        db.add_column(u'timecards_timecard', 'bug_comment_id',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'TimeCard.bug_comment_added'
        db.delete_column(u'timecards_timecard', 'bug_comment_added')


    models = {
        u'timecards.timecard': {
            'Meta': {'object_name': 'TimeCard'},
            'add_to_bug_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bug': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bug_comment_added': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bug_summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['timecards']