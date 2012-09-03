# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from wikiforum.models import Post, History
import json

def convert_set_to_json (data):
    message = {}
    value = []
    for item in data:
        value.append ({"title": item.title})
    message ['items'] = value
    return json.dumps (message)

def find_father (post_id):
    post = Post.objects.get (pk = post_id)
    print "current post: " + post.title
    try:
        pre_post = Post.objects.get (pk = post.pre_post_id)
        print "pre post: " + pre_post.title
    except:
        return None
    return pre_post

def find_ancestor (post_id):
    while True:
        try:
            p = find_father (p.pk)
            if not find_father (p.pk):
                break
            return p
        except: return "Error"

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

@login_required
def body_overview (request, post_id):
    try:
        cur = Post.objects.get (pk = post_id)
        # p = find_father (post_id)
        # n = find_children (post_id)
        # data = convert_set_to_json (n)
        # return HttpResponse (data, mimetype="application/json")
        message = {}
        message ['items'] = cur.body
        data = json.dumps (message)
        return HttpResponse (data, mimetype="application/json")
    except:
        return HttpResponse ("Error")

@login_required
def history_overview (request, history_id):
    try:
        history = History.objects.get (pk = history_id)
        message = {}
        message ['items'] = history.body
        data = json.dumps (message)
        return HttpResponse (data, mimetype="application/json")
    except Exception as e:
        print e
        return HttpResponse ("Error")

@login_required
def tree_view (request, post_id):
    try:
        p = find_ancestor (post_id)
        return HttpResponse (p)
    except Exception as e:
        print e
        return HttpResponse ("Error")

