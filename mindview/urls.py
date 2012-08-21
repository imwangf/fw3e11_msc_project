from django.conf.urls import *

urlpatterns = patterns ('mindview.views',
    url (r'^(?P<post_id>[^/]+)/$', 'body_overview'),
)
