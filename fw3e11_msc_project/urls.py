from django.conf.urls import patterns, include, url

from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import password_reset

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url (r'^wikiforum/', include ('wikiforum.urls')),
    url (r'^accounts/', include ('accounts.urls')),
    url (r'^mindview/', include ('mindview.urls')),
    url (r'^$', direct_to_template,
        {'template': 'index.html'}),
    # Examples:
    # url(r'^$', 'fw3e11_msc_project.views.home', name='home'),
    # url(r'^fw3e11_msc_project/', include('fw3e11_msc_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
