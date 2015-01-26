# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TimeCard.end'
        db.alter_column(u'timecards_timecard', 'end', self.gf('django.db.models.fields.TimeField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'TimeCard.end'
        raise RuntimeError("Cannot reverse this migration. 'TimeCard.end' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'TimeCard.end'
        db.alter_column(u'timecards_timecard', 'end', self.gf('django.db.models.fields.TimeField')())

    models = {
        u'timecards.timecard': {
            'Meta': {'object_name': 'TimeCard'},
            'add_to_bug_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bug': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bug_comment_added': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bug_summary': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['timecards']