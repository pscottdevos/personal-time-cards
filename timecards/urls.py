from django.conf.urls import patterns, include, url
from timecards import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ga.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'last_month/$', views.last_month_report_view, {}, 'last_month_report'),
)
