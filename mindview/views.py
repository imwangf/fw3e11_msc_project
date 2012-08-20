# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from wikiforum.models import Post

def find_father (post_id):
    post = Post.objects.get (pk = post_id)
    print "current post: " + post.title
    try:
        pre_post = Post.objects.get (pk = post.pre_post_id)
        print "pre post: " + pre_post.title
    except:
        return None
    return pre_post

def find_children (post_id):
    post = Post.objects.get (pk = post_id)
    print "current post: " + post.title
    try:
        next_posts = Post.objects.filter (pre_post_id = post_id)
        for next_post in next_posts:
            print "next post: " + next_post.title
    except:
        return None
    return next_posts

def find (request, post_id):
    try:
        p = find_father (post_id)
        n = find_children (post_id)
        return HttpResponse ("ok")
    except:
        return HttpResponse ("Error")

