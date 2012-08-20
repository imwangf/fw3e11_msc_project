from django.contrib.auth.models import User
from django.contrib import admin

admin.site.unregister (User)
admin.site.register (User)
