from django.conf.urls import *
from django.contrib.auth import views as auth_views
from django.views.generic.simple import redirect_to


urlpatterns = patterns ('accounts.views',
        url (r'^$', redirect_to, {'url': '/'}),
    url (r'^register/$', 'register'),
    url (r'^login/$', 'login_view'),
    url (r'^logout/$', 'logout_view'),
    url (r'^change_password/$', auth_views.password_change, name='auth_password_change'),
    url (r'^change_password/done/$', auth_views.password_change_done, name='auth_password_change_done'),
    #url (r'^reset_password/$', 'reset_password'),

    url (r'^users/$', 'find_user'),
    url (r'^users/(?P<username>[^/]+)/$', 'user_view'),

    url (r'^notification/$', 'request_note'),

)
