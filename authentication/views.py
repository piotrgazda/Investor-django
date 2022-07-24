from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import redirect, render

from authentication.models import UserProfile
from authentication.registration import register_user

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)



def user_log(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        username, password = form.cleaned_data['username'], form.cleaned_data['password']
        if User.objects.filter(username=username).exists():
            authenticated_user = authenticate(username=username,
                                              password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('home')
            else:
                return HttpResponse("Invalid password!")
        else:
            user = register_user(login=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
