from django.conf.urls import patterns, include, url
from timecards import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ga.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'last_month_report/$', views.last_month_report_view, {}, 'last_month_report'),
    url(r'this_month_report/$', views.this_month_report_view, {}, 'this_month_report'),
    url(r'this_week_report/$', views.this_week_report_view, {}, 'this_week_report'),
    url(r'timesheet_report/$', views.timesheet_report, {}, 'timesheet_report'),
    url(r'update_bug_info/$', views.update_bug_info_view, {}, 'update_bug_info'),
)
