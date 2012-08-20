# Create your views here.

from wikiforum.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.db import transaction

forum = Forum.objects.get_or_create (name = "fw3e11-forum")

from django import forms
class SearchForm (forms.Form):
    search_text = forms.CharField (label=False)

def new_pk ():
    if Post.objects.all ():
        last_pk_obj = Post.objects.all ().order_by ('-pk') [0]
        pk = last_pk_obj.pk + 1
    else:
        pk = 1
    return pk

########################################
def request_test (request):
    # print dir(RequestContext)
    context_instance = RequestContext (request)
    print context_instance.dicts[2]['user']
    # which will return 'test' -- a username
########################################

# Search
@login_required
def search (request):
    if request.method == 'POST':
        form = SearchForm (request.POST)
        if not form.is_valid ():
            return render_to_response ("wikiforum/search.html", locals (), context_instance = RequestContext (request))
        else:
            search_text = form.cleaned_data ['search_text']
            title_result = Post.objects.filter (title__icontains = search_text)
            # print type(title_result)
            body_result = Post.objects.filter (body__icontains = search_text)
            new_post = Post (pk = new_pk ())
            return render_to_response ("wikiforum/search.html", locals (), context_instance = RequestContext (request))
    form = SearchForm ()
    return render_to_response ("wikiforum/search.html", locals (), context_instance = RequestContext (request))

# Edit
@login_required
def post_edit (request, post_id):
    # draw existing data, to be modified
    try:
        post = Post.objects.get (pk = post_id)
        title = post.title
        body = post.body
        tags = " ".join ([tag.name for tag in post.tags.all ()])
    # New Post
    except Post.DoesNotExist:
        title = ""
        body = ""
        tags = ""
    return render_to_response ("wikiforum/edit.html", locals (), context_instance = RequestContext (request))

# Reply
@login_required
def post_reply (request, post_id):
    post = Post.objects.get (pk = post_id)
    u = User.objects.get (username = request.session ['username'])
    new_post = Post (pk = new_pk (),
            forum = forum [0],
            title = "re: " + post.title,
            body = "",
            modified_by = u,
            pre_post = post)
    request.session ['pre_post'] = post.pk
    return render_to_response ("wikiforum/reply.html", locals (), context_instance = RequestContext (request))

# Save
def post_save (request, post_id):
    title = request.POST ['title']
    body = request.POST ['body']
    tag_list = []
    u = User.objects.get (username = request.session ['username'])
    if 'tags' in request.POST:
        tags = request.POST ['tags']
        tag_list = [Tag.objects.get_or_create (name = tag) [0] \
                for tag in tags.split ()]
    # Edit Exising Case
    try:
        post = Post.objects.get (pk = post_id)
        # title
        post.title = title
        # tags
        deleted_tags = set (post.tags.all ()) - set (tag_list)
        for tag in tag_list:
            post.tags.add (tag)
        for tag in deleted_tags:
            post.tags.remove (tag)
        post.save ()
        # sid = transaction.savepoint ()
        # body
        if post.body == body:
            return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")
        else: post.body = body
        post.save ()
    # Post New Case
    except Post.DoesNotExist:
        # reply case
        try:
            pre_post = Post.objects.get (pk = request.session ['pre_post'])
            post = Post (title = "re: " + pre_post.title,
                    body = "",
                    forum = forum [0],
                    modified_by = u,
                    pre_post = pre_post)
        except KeyError:
            post = Post (title = "New post",
                    body = "",
                    forum = forum [0],
                    modified_by = u)
        # if
        if not title == "":
            post.title = title
        post.body = body
        if post.body == "":
            return HttpResponse ("Body can't be null.")
        post.save ()
        # deal tags
        for tag in tag_list:
            post.tags.add (tag)
        try:
            del request.session ['pre_post']        
        except:
            pass
    try:
        post_obj = Post.objects.get (pk = post_id)
        History.objects.create (post = post_obj, body = post.body, modified_by = u)
    except: pass
    return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")

# View
@login_required
def post_view (request, post_id):
    try:
        post = Post.objects.get (pk = post_id)
        body = post.body
        tags = post.tags.all ()
        related_next_posts = []
        # if you want create new one
        u = User.objects.get (username = request.session ['username'])
        new_post = Post (pk = new_pk (),
            forum = forum [0],
            title = "re: " + post.title,
            body = "",
            modified_by = u) 
        ###############################
        if Post.objects.filter (pre_post_id = post.pk):
            related_next_posts = [p for p in Post.objects.filter (pre_post_id = post.pk)]

        try:
            Post.objects.get (pk = post.pre_post_id)
            related_pre_post = Post.objects.get (pk = post.pre_post_id)
            # print "pre: " + related_pre_post.title
        except Post.DoesNotExist:
            # print "pre: None"
            pass
        # pre_post is unique ####################
        return render_to_response ("wikiforum/view.html", locals (), context_instance = RequestContext (request))
    except Post.DoesNotExist:
        return HttpResponse ("Error! Post Does Not Exist.")

@login_required
def tag_view (request, tag_name):
    try:
        tag = Tag.objects.get (name = tag_name)
        posts = tag.post_set.all ()
    except:
        return HttpResponse ("No tag named" + tag_name)
    return render_to_response ("wikiforum/tag.html", locals (), context_instance = RequestContext (request))

@login_required
def history_view (request, post_id):
    history_dict = {}
    try:
        post_obj = Post.objects.get (pk = post_id)
        history_list = History.objects.filter (post = post_obj)
    except Post.DoesNotExist:
        pass
    return render_to_response ("wikiforum/history.html", locals (), context_instance = RequestContext (request))

