
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings

from datetime import datetime

from dashboard.models import Messages

def index(request):
    context_dict = {}
    context_dict['hi'] = 'hi'
    context_dict['data'] = Messages.objects.all()[::-1]
    response = render(request, 'dashboard/index.html', context_dict)

    #response.set_cookie("my_cookie","hello world")
    #print request.COOKIES.get('my_cookie1','N/A')
    print request.COOKIES

    visits = int(request.COOKIES.get('visits','1'))

    if 'last_visit' in request.COOKIES:
        last_visit = request.COOKIES['last_visit']
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        #more than one day since the last visit
        if (datetime.now() - last_visit_time).seconds > 10:
            response.set_cookie('visits',visits+1)
            response.set_cookie('last_visit', datetime.now())
        else:
            pass
    else:
        response.set_cookie('last_visit',datetime.now())

    return response


def login(request):
    context_dict = {}
    return render(request, 'dashboard/login.html', context_dict)    