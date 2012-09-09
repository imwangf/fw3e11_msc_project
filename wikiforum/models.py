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
    modified_by = models.ForeignKey (User) # this is always the first creator
    pre_post = models.ForeignKey ('self', blank = True, null = True, related_name = '+')
    is_secure = models.BooleanField (default = False)

    def __unicode__ (self):
        return self.title

class Comment (models.Model):
    post = models.ForeignKey (Post)
    content = models.TextField ()
    modified = models.DateTimeField ('Modified', auto_now_add = True)
    modified_by = models.ForeignKey (User)

    def num (self):
        return sum ([t.num() for t in self.post_set.all ()])

class Tag (models.Model):
    name = models.CharField (max_length = 200, primary_key = True)

    def __unicode__ (self):
        return self.name

class History (models.Model):
    post = models.ForeignKey (Post)
    title = models.CharField (max_length = 200)
    body = models.TextField ()
    modified = models.DateTimeField ('Modified', auto_now_add = True)
    modified_by = models.ForeignKey (User)
    is_accepted = models.BooleanField ()
    is_processed = models.BooleanField (default = False)
    processed_by = models.ForeignKey (User, blank = True, null = True, related_name = '+')
    current_version = models.BooleanField (default = False)

    def __unicode__ (self):
        return "History of \"" + self.post.title + "\""

