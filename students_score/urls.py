from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'students_score.views.home', name='home'),
    # url(r'^students_score/', include('students_score.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^students/', include('students.urls')),
    url(r'^', include('students.urls')),
    url(r'^chaining/', include('smart_selects.urls'))
)
urlpatterns += staticfiles_urlpatterns()
