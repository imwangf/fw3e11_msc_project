from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Forum (models.Model):
    name = models.CharField (max_length = 200, primary_key = True)
    
    def __unicode__ (self):
        return self.name

class Post (models.Model):
    forum = models.ForeignKey (Forum)
    title = models.CharField (max_length = 200)
    body = models.TextField ()
    body_html = models.TextField ()
    tags = models.ManyToManyField ('Tag')
    modified = models.DateTimeField ('Modified', auto_now_add = True)
    modified_by = models.ForeignKey (User)
    pre_post = models.ForeignKey ('self', blank = True, null = True, related_name = '+')
    #next_posts = models.ForeignKey ('self', blank = True, null = True, related_name = '+')

    def __unicode__ (self):
        return self.title

class Tag (models.Model):
    name = models.CharField (max_length = 200, primary_key = True)

    def __unicode__ (self):
        return self.name

class History (models.Model):
    post = models.ForeignKey (Post)
    body = models.TextField ()
    modified = models.DateTimeField ('Modified', auto_now_add = True)
    modified_by = models.ForeignKey (User)

    def __unicode__ (self):
        return "History of \"" + self.post.title + "\""

