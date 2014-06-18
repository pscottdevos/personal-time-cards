import models
from django.contrib import admin
from django.db.models import Sum

# Register your models here.

class TimeCardAdmin(admin.ModelAdmin):
    fields = ('date', 'start', 'end', 'code', 'description')
    list_display = fields + ( 'short_description', )

class TcCodeAdmin(admin.ModelAdmin):
    fields = ('code', 'description', 'project', 'status')
    list_display = fields + ('hours_last_week', )


admin.site.register(models.TcProject)
admin.site.register(models.TcCode, TcCodeAdmin)
admin.site.register(models.TimeCard, TimeCardAdmin)
