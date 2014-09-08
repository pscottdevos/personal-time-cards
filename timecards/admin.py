import models
from django.contrib import admin
from django.db.models import Sum

# Register your models here.


class TimeCardAdmin(admin.ModelAdmin):
    fields = ( 'date', 'start', 'end', 'bug', 'bug_summary', 'add_to_bug_comments', 'description', )
    list_display = ( 'date', 'start', 'end', 'anchor', 'short_description', )
    ordering = ('-date', '-start')
    readonly_fields = ('bug_summary',)

    def anchor(self, object):
        return object.get_anchor()
    anchor.short_description = "Bug"
    anchor.allow_tags = True

admin.site.register(models.TimeCard, TimeCardAdmin)
