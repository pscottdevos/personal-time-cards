# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TimeCard.add_to_bug_comments'
        db.add_column(u'timecards_timecard', 'add_to_bug_comments',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'TimeCard.bug_comment_id'
        db.add_column(u'timecards_timecard', 'bug_comment_id',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TimeCard.add_to_bug_comments'
        db.delete_column(u'timecards_timecard', 'add_to_bug_comments')

        # Deleting field 'TimeCard.bug_comment_id'
        db.delete_column(u'timecards_timecard', 'bug_comment_id')


    models = {
        u'timecards.timecard': {
            'Meta': {'object_name': 'TimeCard'},
            'add_to_bug_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bug': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bug_comment_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bug_summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['timecards']