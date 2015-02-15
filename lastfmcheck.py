import json
import urllib.parse, urllib.error
import http.client
import bs4

def crLFMRequest(lArtist="", lAlbum=""):
  '''Build request to send it to lastFM later

     args:
       lArtist - string, should represent Artist name
       lAlbum  - string, should represent Album name

     returns request string which applied to http query OR false
  '''
  data = json.load(open('partwork.conf','r')) # load conffile
  sApiKey  = data['lastFM']['apikey']
  if lArtist and ((lAlbum != 'Single') and (lAlbum != 'single') and lAlbum):
    sArtist = urllib.parse.quote_plus(lArtist.encode('utf-8')) # this done to cyrillic works
    sAlbum  = urllib.parse.quote_plus(lAlbum.encode('utf-8')) # this done to cyrillic works
    params  = {'method' : 'album.getinfo', 'api_key' : sApiKey, 'artist' : sArtist, 'album' : sAlbum}
    return urllib.parse.unquote(urllib.parse.urlencode(params))
  elif lArtist:
    sArtist = urllib.parse.quote_plus(lArtist.encode('utf-8')) # this done to cyrillic works
    params  = {'method' : 'artist.getinfo', 'artist' : sArtist, 'api_key' : sApiKey}
    return urllib.parse.unquote(urllib.parse.urlencode(params))
  else:
    return False


def crLFMQuery(LFMRequest=""):
  '''Build query to requests. Split from request cause one query may treat
     many requests.

     args:
       LFMRequest - result from crLFMRequest(lArtist, lAlbum) function

     returns lastFM server answer which contains some URLs that points to artwork
  '''
  if LFMRequest:
    LFMUrl = 'ws.audioscrobbler.com'
    cConn = http.client.HTTPConnection(LFMUrl)
    cConn.request('GET', '/2.0/?' + LFMRequest)
    cResult = cConn.getresponse()
    cConn.close()
    return cResult.read()
  else:
    return False


def parseImgURL(query="", iSize="large"):
  '''Parse query and cut URLs with images from it.

     args:
       query - result from crLFMQuery(LFMRequest="") function
       iSize - desired image size. Can be large, medium, small. Default is large.

     returns URL which point to image file
  '''
  if query:
    bsSoup = bs4.BeautifulSoup(query, features='xml')
    if bsSoup and not bsSoup.find('error', code=6):
      #print('image URL is: ', bsSoup.find('image', size='large').text)
      return bsSoup.find('image', size=iSize).text
    else:
      print('We cannot find suitable artwork URL for that song, sorry')
      return False
  else:
    return False

def process(artist="",album=""):
  '''Call all functions and return artwork URL.

     args:
       lArtist - string, should represent Artist name
       lAlbum  - string, should represent Album name

     returns artwork URL
  '''
  return parseImgURL(
                     crLFMQuery(
                                crLFMRequest(artist,album)))

if __name__ == "__main__":
  data = {
    "first":
      { 'artist':'Metallica',
        'album':'Master of Puppets'},
    "second":
      { 'artist':'Наутилус Помпилиус',
        'album':'Чужая земля'}
  }
  for k,v in data.items():
    request = crLFMRequest(v['artist'],v['album'])
    query = crLFMQuery(request)
    url = parseImgURL(query)
    print('URL for %s album "%s" is %s' % (v['artist'],v['album'],url))


