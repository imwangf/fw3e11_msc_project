# Create your views here.

from wikiforum.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.db import transaction
import json

forum = Forum.objects.get_or_create (name = "fw3e11-forum")

from django import forms
class SearchForm (forms.Form):
    search_text = forms.CharField (label=False,widget=forms.TextInput(attrs={'data-provide':'typeahead','autocomplete':'off', 'placeholder': 'Search posts by title or content'}))

def new_pk ():
    if Post.objects.all ():
        last_pk_obj = Post.objects.all ().order_by ('-pk') [0]
        pk = last_pk_obj.pk + 1
    else:
        pk = 1
    return pk

def to_html (body):
    body_html = body.replace("\r\n", "<br/>")
    body_html = body.replace("\n", "<br/>")
    body_html = body.replace("\r", "<br/>")
    return body_html


########################################
def request_test (request):
    # print dir(RequestContext)
    context_instance = RequestContext (request)
    print context_instance.dicts[2]['user']
    # which will return 'test' -- a username
########################################


@login_required
def get_all_title (request):
    try:
        message = {}
        title = []
        title_list = [ttl.title for ttl in Post.objects.all ()]
        title_list = list (set (title_list)) # remove duplicated titles
        message ['items'] = title_list
        data = json.dumps (message)
        return HttpResponse (data, mimetype="application/json")
    except Exception as e:
        print e
        return HttpResponse ("Error")

@login_required
def get_all_tags (request):
    try:
        message = {}
        tags = []
        tag_list = [tgs.name for tgs in Tag.objects.all ()]
        message ['items'] = tag_list
        data = json.dumps (message)
        return HttpResponse (data, mimetype="application/json")
    except Exception as e:
        print e
        return HttpResponse ("Error")


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
        body_html = post.body_html
        tags = " ".join ([tag.name for tag in post.tags.all ()])
    # New Post
    except Post.DoesNotExist:
        title = ""
        body = ""
        body_html = ""
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
            body_html = "",
            modified_by = u,
            pre_post = post)
    request.session ['pre_post'] = post.pk
    return render_to_response ("wikiforum/reply.html", locals (), context_instance = RequestContext (request))

# Save
def post_save (request, post_id):
    title = request.POST ['title']
    body = request.POST ['body']
    try:
        is_secure = request.POST ['is_secure']
    except: pass
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
        body_html = to_html (body)

        post.body = body
        post.body_html = body_html
        # textarea
        #re.sub("\r", "<br/>", post.body)
                # ########
        if post.is_secure == True:
            if u.is_superuser or u == post.modified_by:
                post.save ()
                history = History.objects.create (post = post, title = title, body = post.body, modified_by = u, is_accepted = True, current_version = True)
                hcs = History.objects.filter (post = post, current_version = True)
                for hc in hcs:
                    hc.current_version = False
                    hc.save ()
                history.current_version = True
                history.save ()
            else:
                History.objects.create (post = post, title = title, body = post.body, modified_by = u, is_accepted = False)
        else:
            post.save ()
            history = History.objects.create (post = post, title = title, body = post.body, modified_by = u, is_accepted = True, current_version = True)
            hcs = History.objects.filter (post = post, current_version = True)
            for hc in hcs:
                hc.current_version = False
                hc.save ()
            history.current_version = True
            history.save ()

    # Post New Case
    except Post.DoesNotExist:
        # reply case
        try:
            pre_post = Post.objects.get (pk = request.session ['pre_post'])
            try:
                post = Post (title = "re: " + pre_post.title,
                        body = "",
                        body_html = "",
                        forum = forum [0],
                        modified_by = u,
                        pre_post = pre_post,
                        is_secure = is_secure)
            except:
                post = Post (title = "re: " + pre_post.title,
                        body = "",
                        body_html = "",
                        forum = forum [0],
                        modified_by = u,
                        pre_post = pre_post,
                        is_secure = False)
        # create case
        except KeyError:
            try:
                post = Post (title = "New post",
                        body = "",
                        body_html = "",
                        forum = forum [0],
                        modified_by = u,
                        is_secure = is_secure)
            except:
                post = Post (title = "New post",
                        body = "",
                        body_html = "",
                        forum = forum [0],
                        modified_by = u,
                        is_secure = False)
        # if
        if not title == "":
            post.title = title
        if body == "":
            return HttpResponse ("Body can't be null.")
        # textarea
        body_html = to_html (body)

        post.body = body
        post.body_html = body_html
        # ########
        post.save ()
        History.objects.create (post = post, title = title, body = post.body, modified_by = u, is_accepted = True, current_version = True)
        # deal tags
        for tag in tag_list:
            post.tags.add (tag)
        try:
            del request.session ['pre_post']        
        except:
            pass
    # history part moved
    return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")

# View
@login_required
def post_view (request, post_id):
    try:
        post = Post.objects.get (pk = post_id)
        body_html = post.body_html
        tags = post.tags.all ()
        related_next_posts = []
        comments = Comment.objects.filter (post = post)
        # if you want create new one
        u = User.objects.get (username = request.session ['username'])
        new_post = Post (pk = new_pk (),
            forum = forum [0],
            title = "re: " + post.title,
            body = "",
            body_html = "",
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

@login_required
def comment_save (request, post_id):
    try:
        post = Post.objects.get (pk = post_id)
        content = request.POST ['content']
        u = User.objects.get (username = request.session ['username'])
        comment = Comment (post = post,
                content = content,
                modified_by = u)
        comment.save ()
    except Exception as e:
        print e
    return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")

@login_required
def comment_delete (request, post_id, comment_id):
    try:
        comment = Comment.objects.get (pk = comment_id)
        if comment.modified_by.username == request.session ['username']:
            comment.delete ()
        else:
            pass
    except Exception as e:
        print e
    return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")

@login_required
def history_rollback (request, post_id, history_id):
    try:
        post = Post.objects.get (pk = post_id)
        history = History.objects.get (pk = history_id)
        u = User.objects.get (username = request.session ['username'])
        if not history.is_accepted:
            return HttpResponseRedirect (".")
        if u.is_superuser:
            post.body = history.body
            post.body_html = to_html (post.body)
            post.save ()
            history = History.objects.create (post = post, body = "[rollback by " + u.username + "]:\r\n" + post.body, modified_by = u, is_accepted = True, current_version = True)
            hcs = History.objects.filter (post = post, current_version = True)
            for hc in hcs:
                hc.current_version = False
                hc.save ()
            history.current_version = True
            post.save ()
            history.save ()

        else:
            return HttpResponse ("Permission denied.")
    except Exception as e:
        print e
    return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")

@login_required
def request_accept (request, post_id, history_id):
    try:
        post = Post.objects.get (pk = post_id)
        history = History.objects.get (pk = history_id)
        u = User.objects.get (username = request.session ['username'])
        if u.is_superuser or u == post.modified_by:
            post.title = history.title
            post.body = history.body
            post.body_html = to_html (post.body)
            history.processed_by = u
            history.is_accepted = history.is_processed = True
            hcs = History.objects.filter (post = post, current_version = True)
            for hc in hcs:
                hc.current_version = False
                hc.save ()
            history.current_version = True
            post.save ()
            history.save ()
        else:
            return HttpResponse ("Permission denied.")
    except Exception as e:
        print e
    return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")

@login_required
def request_deny (request, post_id, history_id):
    try:
        post = Post.objects.get (pk = post_id)
        history = History.objects.get (pk = history_id)
        u = User.objects.get (username = request.session ['username'])
        if u.is_superuser or u == post.modified_by:
            history.processed_by = u
            history.is_accepted = False
            history.is_processed = True
            history.save ()
        else:
            return HttpResponse ("Permission denied.")
    except Exception as e:
        print e
    return HttpResponseRedirect ("/wikiforum/posts/" + post_id + "/")
