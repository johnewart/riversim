__author__ = 'jewart'

from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect

def do_login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)

    return redirect("/")

def _get_tile(request):
   format, image = settings.MAP_SERVICE.dispatchRequest(
           request.GET, request.path, request.method, 
           request.get_host()
   )
   return HttpResponse(str(image), mimetype=format)

def wms(request):
    if request.GET.get('request') == 'GetFeatureInfo':
        return HttpResponse(status=404)
    else:
        return _get_tile(request)
