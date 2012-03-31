from ui.models import *
from django.db import models
import urllib2
import urllib
from django.template.defaultfilters import slugify
import datetime
import time
import re

def queue_url(url, should_wait, **args):
    try:
        return ScrapeReq.objects.get(url=url, fulfilled=True).result
    except Exception as e:
        pass
    
    priority = args['priority'] if 'priority' in args else 0
    r = ScrapeReq(url=url, priority=priority)
    
    if should_wait:
        
        time.sleep(2)
        #r.result = urllib2.urlopen(url).read()
        
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1081.2 Safari/536.5')]
        r.result = opener.open(url).read()
        
        
        r.fulfilled = True
        r.requested = datetime.datetime.now()
        r.save()
        
        return r.result
    else:
        r.fulfilled = False
        r.save()
        return None 

def albums_for_artist(artist, obj):
    info_for_artist(artist, obj)
    
    if obj.allmusic_name:
        allm_disco_url = 'http://www.allmusic.com/artist/%s/discography' % obj.allmusic_name
        contents = queue_url(allm_disco_url, True)
        
        r = re.compile(r'<tr class="visible" id="trlink">.+?</tr>', re.DOTALL)
        rows = re.findall(r, contents)
        
        def pick_albums(rows):
            for row in rows:
                album_pick = 'album pick' in row
        
                stars = 0
                rating = re.search(r'stars/st_r(\d).gif', row)
                if rating == None:
                    rating = 0
                else:
                    rating = (float(rating.group(1)) + 1) / 2
        
                name_r = r'<td class="cell"><a href="http://www.allmusic.com/album/[^"]+">([^<]+)</a></td>'
                name = re.search(name_r, row).group(1)
                
                yield {
                    'rating':rating, 
                    'name': name,
                    'album_pick': album_pick,
                }
        
        for albumdata in pick_albums(rows):
            try:
                al = Album.objects.get(slug=slugify(albumdata['name']), artist=obj)
            except Album.DoesNotExist:
                print albumdata['name']
                al = Album(name=albumdata['name'], artist=obj)
                al.allmusic_pick = albumdata['album_pick']
                al.allmusic_rating = albumdata['rating']
            
            al.save()
    
    # Download the album list off rym
    rym_name = slugify(artist).replace('-', '_')
    rym_artist_page = queue_url('http://rateyourmusic.com/artist/%s' % rym_name, True)
    #print rym_artist_page
    # album_ctx_re = r'<th[^>]+>Released</th>(.+?)(?:<th[^>]+>Released</th>)?'
    album_ctx_re = r'>Released<(.+?)(?:>Released<|$)'
    rym_artist_page_ctx = re.findall(re.compile(album_ctx_re, re.DOTALL), rym_artist_page)
    #print rym_artist_page_ctx
    if rym_artist_page_ctx:
        rym_artist_page_ctx = rym_artist_page_ctx[0]
        #print rym_artist_page_ctx
        #rym_album_re = r'<tr[^>]+>\s*<td[^>]+>\s*<span[^>]+ title="\d+">(\d+)</span></td>\s*<td[^>]*>(<b>)?<a href="([^">]+)"\s*>([^>]+)</a>\s*(</b>?)\s*</td>.+?<td style="text-align:center;">\s*(\d*)\s*</td>.+?<td  [^>]*>\s*(\d*)\s*</td>.+?(class="abmrat" style="width:(\d+)px;")?.+?(class="abmpop" style="width:(\d+)px;").+?<td><div[^>]*>([\d.]+)</div>'
        rym_album_re = r'<tr[^>]+>.*?<td[^>]+>(.*?)</td>.*?<td[^>]+>(.*?)</td>.*?<td[^>]+>(.*?)</td>.*?<td[^>]+>(.*?)</td>.*?<td[^>]+>(.*?)</td>.*?<td[^>]+>(.*?)</td>.*?<td[^>]+>(.*?)</td>'
        occs = re.findall(re.compile(rym_album_re, re.DOTALL), rym_artist_page_ctx)
        for occ in occs:
            print '======'
            print occ[0]
            print '- - -'
            print occ[1]
            print '- - -'
            print occ[2]
            print '- - -'
            print occ[3]
            print '- - -'
            print occ[4]
            print '- - -'
            print occ[5]
            print '- - -'
            print occ[6]
            
            namehtml = occ[1]
            nametxt = reextract(namehtml, r'>([><]+)</a>')
            
            if not nametxt:
                continue
            
            try:
                al = Album.objects.get(slug=slugify(nametxt), artist=obj)
            except Album.DoesNotExist:
                print albumdata['name']
                al = Album(name=albumdata['name'], artist=obj)
            
            datehtml = occ[0]
            datetxt = reextract(datehtml, r'>\d+<')
            if datetxt:
                al.rym_year = int(datetxt, 10)
            
            
            # issueshtml = occ[2]
            reviewshtml = occ[3].replace(',', '')
            if reviewshtml:
                al
            ratingshtml = occ[4].replace(',', '')
            charthtml = occ[5]
            
            al.save()
            
            
            
    
    '''
    <tr id="tr25213"  >
                     <td  style="text-align:center;"><span style="font-size: 1.1em; font-weight:bold;
    color:gray;" title="1973">1973</span></td>
                     <td ><b><a href="/release/album/dave_holland/conference_of_the_birds/" >Conference of the Birds</a> </b>
                       </td>
                     <td class="small"><a id="issueLink25213" href="javascript:showIssues(25213);" class="tinybutton">3 issues</a></td>
    
                     <td style="text-align:center;">23</td>
    
                     <td  style="width:5em;text-align:center;padding:5px;">544</td><td style="width:100%;padding:0;"><div title="rating" class="abmrat" style="width:77px;">&nbsp;</div><div title="popularity" class="abmpop" style="width:67px;">&nbsp;</div></td>
                     <td><div class="medium">3.97</div></td><td class="center"><a class="artist_rate_act" href="/release/album/dave_holland/conference_of_the_birds/">rate</a></td>
    '''
    
def info_for_artist(artist, obj):
    try:
        
        # Download allmusic
        allm_search = queue_url('http://www.allmusic.com/search/artist/%s/filter:all/exact:0' % urllib.quote(artist), True)
        #print allm_search
        ss = re.findall(r'<a href="http://www.allmusic.com/artist/([^/"]+)">', allm_search)
        #print ss
        if ss:
            s = ss[0]
            obj.allmusic_name = s
            
            # Get the biography
            bio = re.findall(r'<p class="text">(.+?)</p>', queue_url('http://www.allmusic.com/artist/%s/biography' % s, True))
            #print bio
            if bio:
                obj.allmusic_bio = bio[0]
    finally:
        obj.save()