# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
import os

colors = ['#006DB8', '#75C695', '#85D2DD', '#8D6538', '#C4A2CB',
          '#008B59', '#F598AA', '#652D91', '#FECD08', '#00B1B0',
          '#9A983A', '#F79447']

def sorter(s):
    bus = s.split('_')[0]
    if bus == '51B':
        return 51
    if bus == 'F':
        return 100
    return int(bus)

# Create your views here.
def index(request):
    # return HttpResponse("status=201")
    path = "app/static/gpx"
    gpx_list = os.listdir(path)
    gpx_list.sort(key=sorter)
    return render(request, 'app/index.html', {'gpx_list': gpx_list, 'colors': colors})
