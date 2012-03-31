from django.db import models
from django.template.defaultfilters import slugify
import math
def erf(x):
    # save the sign of x
    sign = 1 if x >= 0 else -1
    x = abs(x)

    # constants
    a1 =  0.254829592
    a2 = -0.284496736
    a3 =  1.421413741
    a4 = -1.453152027
    a5 =  1.061405429
    p  =  0.3275911

    # A&S formula 7.1.26
    t = 1.0/(1.0 + p*x)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*math.exp(-x*x)
    return sign*y

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
    slug = models.SlugField()
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
    rym_year = models.IntegerField(default=0)
    rym_numratings = models.IntegerField(default=0)
    rym_numreviews = models.IntegerField(default=0)
    
    rym_overall = models.FloatField(default=0)
    rym_rating = models.IntegerField(default=0)
    rym_popularity = models.IntegerField(default=0)
    
    def combinedscore(self):
        
        # So a 5 on rym is roughly equal to a 6 on allmusic
        # a 4 ~ 4.5
        # 3.8 ~ 4
        # 3.5 ~ 3
        
        if self.rym_overall:
            rym = erf(self.rym_overall - 3.4)*3 + 3 #1 + self.rym_overall
        else:
            rym = None
        
        if self.allmusic_rating != -1:
            alm = self.allmusic_rating
        else:
            alm = None
        
        if rym == None and alm == None:
            return 0.0
        if rym == None:
            rym = alm
        if alm == None:
            alm = rym
        
        return math.sqrt(rym * alm)

class Track(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super(Track, self).save(*args, **kwargs)
    
    album = models.ForeignKey('Album')
