import models
from django.contrib import admin

# Register your models here.

class TimeCardAdmin(admin.ModelAdmin):
    fields = ('date', 'start', 'end', 'code', 'description')
    list_display = ('date', 'start', 'end', 'code', 'hours', 'monthly_hours_for_code_to_date', 'short_description')

class TcCodeAdmin(admin.ModelAdmin):
    fields = ('code', 'description', 'project', 'status')
    list_display = fields + ('monthly_hours_to_date',)

admin.site.register(models.TcProject)
admin.site.register(models.TcCode, TcCodeAdmin)
admin.site.register(models.TimeCard, TimeCardAdmin)
