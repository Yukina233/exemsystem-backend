# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from backend.models import UserList
import json
import os

def notfound(request):
  status = { 'code': 404, 'info': 'not found' }
  return HttpResponse(json.dumps(status), content_type="application/json")

def httpecho(request):
  if request.method == 'POST':
    status = { 'code': 200, 'method': 'post', 'echo': request.POST.get('msg') }
    return HttpResponse(json.dumps(status), content_type="application/json")
  elif request.method == 'GET':
    status = { 'code': 200, 'method': 'get', 'echo': request.GET.get('msg') }
    return HttpResponse(json.dumps(status), content_type="application/json")
  else:
    status = { 'code': 403, 'method': request.method, 'echo': '' }
    return HttpResponse(json.dumps(status), content_type="application/json")