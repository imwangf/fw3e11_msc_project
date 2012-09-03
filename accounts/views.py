# Create your views here.

from wikiforum.models import *
import json

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate, login, logout

from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
class UserCreationFormExtended (UserCreationForm):
    def __init__ (self, *args, **kwargs):
        super (UserCreationFormExtended, self).__init__ (*args, **kwargs)
        ## custom settings
        self.fields ['email'].required = True
        self.fields ['first_name'].required = True
        self.fields ['last_name'].required = True
        self.fields ['username'].regex = r'^[\w._]+$'
        self.fields ['username'].help_text = "Required. 30 characters or fewer. Letters, digits and underscore only."
        self.fields ['password2'].label = "Re-enter password"
        self.fields ['password2'].help_text = ""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save (self, commit = True):
        user = super (UserCreationForm, self).save (commit = False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save ()
        return user

def register (request):
    if request.method == 'POST':
        form = UserCreationFormExtended (request.POST)
        if form.is_valid ():
            new_user = form.save ()
            return render_to_response ("accounts/register_done.html")
    else:
        form = UserCreationFormExtended ()
    return render_to_response ("accounts/register.html", locals (), context_instance = RequestContext (request))

class LoginForm (forms.Form):
    username = forms.CharField (label = "Username")
    password = forms.CharField (label = "Password", widget=forms.PasswordInput(render_value=False))

def login_view (request):
    print request.META['HTTP_USER_AGENT'], request.META['REMOTE_ADDR']
    if request.method == 'POST':
        form = LoginForm (request.POST)
        if form.is_valid ():
            username = request.POST ['username']
            password = request.POST ['password']
            user = authenticate (username=username, password=password)
            if user is not None:
                if user.is_active:
                    login (request, user)
                    request.session ['username'] = username
                    if 'next' in request.GET:
                        return HttpResponseRedirect(request.GET['next'])
                    else:
                        return HttpResponseRedirect ("/")
                else:
                    # Return a 'disabled account' error message
                    return render_to_response ("accounts/is_not_activated.html")
            else:
                # Return an 'invalid login' error message.
                return render_to_response ("accounts/login_error.html")
    else:
        form = LoginForm ()
    return render_to_response ("accounts/login.html", locals (), context_instance = RequestContext (request))

def logout_view (request):
    try:
        logout (request)
        del request.session ['username']
    except:
        pass
    return render_to_response ("accounts/logout_done.html")

@login_required
def user_view (request, username):
    try:
        # 'user' is used in session, so use 'usr' instead.
        usr = User.objects.get (username = username)
        if Post.objects.filter (modified_by = usr):
            posts = Post.objects.filter (modified_by = usr)
        if History.objects.filter (modified_by = usr):
            history_records = History.objects.filter (modified_by = usr)
            cleaned_history_records = []
            cleaned_set = []
            for history_record in history_records:
                if history_record.post_id in cleaned_set:
                    continue
                cleaned_history_records.append (history_record)
                cleaned_set.append (history_record.post_id)

    except User.DoesNotExist:
        return render_to_response ("accounts/user_does_not_exist.html")
    return render_to_response ("accounts/user.html", locals (), context_instance = RequestContext (request))

@login_required
def find_user (request):
    return render_to_response ("accounts/find_user.html", locals (), context_instance = RequestContext (request))

@login_required
def request_note (request):
    try:
        request_notes = []
        u  = User.objects.get (username = request.session ['username'])
        if u.is_superuser:
            request_notes += History.objects.filter (is_accepted = False, is_processed = False)
        else:
            posts = Post.objects.filter (modified_by = u)
            for post in posts:
                request_notes += History.objects.filter (post = post, is_accepted = False, is_processed = False)
        message = {}
        value = []
        for request_note in request_notes:
            value.append ({
                "post_id": request_note.post_id,
                "creator": request_note.post.modified_by.username,
                "title": request_note.title,
                "modified_by": request_note.modified_by.username
                })
        message ['items'] = value
        data = json.dumps (message)
        return HttpResponse (data, mimetype="application/json")
    except Exception as e:
        print e
        return HttpResponse ("No request.")
