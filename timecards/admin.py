import models
from django.contrib import admin
from django.db.models import Sum

# Register your models here.

class TimeCardAdmin(admin.ModelAdmin):
    fields = ('date', 'start', 'end', 'code', 'description')
    list_display = fields + ( 'short_description', )
    ordering = ('-date', '-start')

class TcCodeAdmin(admin.ModelAdmin):
    fields = ('code', 'description', 'project', 'status')
    list_display = fields + ('hours_last_week', )

class TcProjectAdmin(admin.ModelAdmin):
    fields = ('status', 'name')
    ordering = ('status','name')
    list_display = fields + (
        'hours_in_week_1_last_month', 'hours_in_week_2_last_month', 'hours_in_week_3_last_month',
        'hours_in_week_4_last_month', 'hours_in_week_5_last_month'
    )


admin.site.register(models.TcProject, TcProjectAdmin)
admin.site.register(models.TcCode, TcCodeAdmin)
admin.site.register(models.TimeCard, TimeCardAdmin)
