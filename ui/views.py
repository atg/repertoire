from django.shortcuts import render_to_response, redirect
from ui.models import *
from django.db import models
from django.template.defaultfilters import slugify
import scraper
import re
import threading
import lastfm
import django

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

def lastfm_import(req):
    artists = lastfm.getArtists(req.POST['name'])
    artists = [a for a,c in artists if c > 2 and '/' not in a and ',' not in a and '&' not in a]
    # r = '<br>'.join(artists)
    
    return tmpl('lastfm_artist_importer.html', artistnames=artists)
    # return django.http.HttpResponse(r)
def lastfm_import_artists(req):
    artistnames = [p for p in req.POST if req.POST[p] == 'on']
    for a in artistnames:
        try:
            ar = Artist.objects.get(slug=slugify(a))
        except Artist.DoesNotExist:
            ar = Artist(name=a)
            ar.save()
    return redirect('/')

artist_thread = None
def reload_artists():
    global artist_thread
    print 'STARTING PULLDOWN'
    for a in Artist.objects.all():
        print '  %s' % (a.name,)
        scraper.info_for_artist(a.name, a)
        scraper.albums_for_artist(a.name, a)
    print 'ENDING PULLDOWN'
    artist_thread = None
def get_artist_data(req):
    global artist_thread
    artist_thread = threading.Thread(target=reload_artists)
    artist_thread.setDaemon(True)
    artist_thread.start()
    return redirect('/')

def view_artist(req, n):
    a = Artist.objects.get(slug=n)
    scraper.info_for_artist(a.name, a)
    scraper.albums_for_artist(a.name, a)
    return tmpl('artist.html', artist=a)
