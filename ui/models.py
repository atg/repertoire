from django.db import models
from django.template.defaultfilters import slugify

class ScrapeReq(models.Model):
    url = models.URLField(unique=True)
    priority = models.IntegerField()
    fulfilled = models.BooleanField()
    result = models.TextField()
    requested = models.DateField(null=True)

class Artist(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super(Artist, self).save(*args, **kwargs)
    
    # allmusic.com
    allmusic_name = models.CharField(max_length=200)
    allmusic_bio = models.TextField()

ALBUM_STATE_CHOICES = (
    ('w', 'wanted'),
    ('u', 'unclassified'),
    ('i', 'ignored'),
    ('g', 'grabbed'),
    ('d', 'downloaded'),
)
class Album(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super(Album, self).save(*args, **kwargs)
    
    artist = models.ForeignKey('Artist')
    state = models.CharField(choices=ALBUM_STATE_CHOICES, max_length=2, default='u')
    
    # allmusic.com
    allmusic_rating = models.IntegerField(default=-1)
    allmusic_pick = models.BooleanField(default=False)
    
    # rateyourmusic.com
    rym_overall = models.FloatField(default=0)
    rym_numratings = models.IntegerField(default=0)
    rym_numreviews = models.IntegerField(default=0)
    

class Track(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super(Track, self).save(*args, **kwargs)
    
    album = models.ForeignKey('Album')
