__author__ = 'jewart'

from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout

def do_login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)

    return redirect("/")