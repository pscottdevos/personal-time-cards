import models
from django.contrib import admin
from django.db.models import Sum

# Register your models here.


class TimeCardAdmin(admin.ModelAdmin):
    fields = ( 'date', 'start', 'end', 'bug', 'description', )
    list_display = ( 'date', 'start', 'end', 'anchor', 'short_description', )
    ordering = ('-date', '-start')

    def anchor(self, object):
        return object.anchor()
    anchor.short_description = "Bug"
    anchor.allow_tags = True

admin.site.register(models.TimeCard, TimeCardAdmin)
