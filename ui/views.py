from django.shortcuts import render_to_response, redirect
from ui.models import *
from django.db import models
import scraper
import re

def tmpl(n, **others):
    return render_to_response(n, dict({
        'artists': Artist.objects.all(),
        'albums': Album.objects.all(),
        'tracks': Track.objects.all(),
    }.items() + others.items()))

def home(req):
    print Artist.objects.count()
    return tmpl('home.html')
def add_artist(req):
    print req.POST['name']
    a = Artist(name=req.POST['name'])
    a.save()
    
    return redirect('/')
def view_artist(req, n):
    a = Artist.objects.get(slug=n)
    scraper.info_for_artist(a.name, a)
    scraper.albums_for_artist(a.name, a)
    return tmpl('artist.html', artist=a)
