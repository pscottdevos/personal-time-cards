import timecards.urls
from django.conf.urls import patterns, include, url
from django.shortcuts import redirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ga.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(timecards.urls)),
    url(r'^$', lambda *args, **kwargs: redirect('admin/', *args, **kwargs)),
)
