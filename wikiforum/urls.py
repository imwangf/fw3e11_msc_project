from django.conf.urls import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns ('wikiforum.views',
        url (r'^$', redirect_to, {'url': '/wikiforum/search/'}),
    url (r'^search/$', 'search'),

        url (r'^posts/$', redirect_to, {'url': '/'}),
    url (r'^posts/(?P<post_id>[^/]+)/edit/$', 'post_edit'),
    url (r'^posts/(?P<post_id>[^/]+)/reply/$', 'post_reply'),
    url (r'^posts/(?P<post_id>[^/]+)/save/$', 'post_save'),
    url (r'^posts/(?P<post_id>[^/]+)/$', 'post_view'),
    url (r'^posts/(?P<post_id>[^/]+)/edit/history/$', 'history_view'),
    
    url (r'^tags/(?P<tag_name>[^/]+)/$', 'tag_view'),
    
    url (r'^search/request/$', 'request_test'),
    url (r'^search/get_all_title/$', 'get_all_title'),
    url (r'^search/get_all_tags/$', 'get_all_tags'),

    url (r'^posts/(?P<post_id>[^/]+)/comment/save', 'comment_save'),
)
