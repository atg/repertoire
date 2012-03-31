import urllib

def nzbindex_url(album):
    query = album.artist.slug.replace('-', ' ') + album.slug.replace('-', ' ')
    
    q = 'http://nzbindex.com/search/?q=%s&age=&max=25&minage=&sort=agedesc&minsize=50&maxsize=&dq=&poster=&nfo=&hidecross=1&complete=1&hidespam=0&hidespam=1&more=1' % urllib.quote(query)
    
    