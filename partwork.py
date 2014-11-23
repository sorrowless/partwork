# coding=utf-8
__author__ = 'gra2f'

import sys
import os
import tempfile
import argparse
import urllib
import httplib
import bs4
import json
from mutagen import id3, mp3


def createParser():
    '''Create parser for command-line arguments'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', nargs = '+')
    parser.add_argument('-d', '--dir', nargs = '+')
    parser.add_argument('-r', '--recursive', action = 'store_true')
    return parser


def getmp3():
    '''Parse command-line and do all work to find files to artwork and all calls to
        treat with them'''
    # TODO: need some rework, cause this function too big and too difficult to understand
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    # namespaces parsing processed splitly.
    # --file processing
    if namespace.file:
        files = [' '.join(namespace.file)]
        for filename in files:
            print filename
            if not isArtworked(filename):
                tempArtFile = getartwork(parseImgURL(crLFMQuery(crLFMRequest(getTags(filename))), 'large'))
                if tempArtFile:
                    setartwork(filename, tempArtFile)
                else:
                    print 'file', filename, 'not artworked'
            else:
                print 'file', filename, 'already artworked'
    # --dir processing
    if namespace.dir:
        dirs = [' '.join(namespace.dir)]
        if not namespace.recursive:
            if isLocalcovers(dirs[0]):      # if local directory have file that seems to artwork
                localCover = isLocalcovers(dirs[0])
                for file in os.listdir(dirs[0]):
                    if file.endswith('.mp3'):
                        if not isArtworked(dirs[0] + '\\' + file):
                            setartwork(dirs[0] + '\\' + file, localCover)
                        else:
                            print 'file', dirs[0] + '\\' + file, 'already artworked'
            else:                           # if local directory don't have file that seems to artwork
                for file in os.listdir(dirs[0]):
                    if file.endswith('.mp3'):
                        if not isArtworked(dirs[0] + '\\' + file):
                            tempArtFile = getartwork(parseImgURL(crLFMQuery(crLFMRequest(getTags(dirs[0] + '\\' + file))), 'large'))
                            if tempArtFile:
                                setartwork(dirs[0] + '\\' + file, tempArtFile)
                        else:
                            print 'file', dirs[0] + '\\' + file, 'already artworked'
        else:
            print 'Recursive flag enabled'
            for root, dirs, files in os.walk(dirs[0]):
                for file in files:
                    if file.endswith('.mp3'):
                        if not isArtworked(os.path.join(root, file)):
                            if isLocalcovers(root):                     # TODO: need deeply rework, this code isn't optimal
                                setartwork(os.path.join(root, file), isLocalcovers(root))
                            else:
                                tempArtFile = getartwork(parseImgURL(crLFMQuery(crLFMRequest(getTags(os.path.join(root, file)))), 'large'))
                                if tempArtFile:
                                    setartwork(os.path.join(root, file), tempArtFile)
                        else:
                            print 'file', os.path.join(root, file), 'already artworked'


def isLocalcovers(dir):
    ''' Check, is in dir, pass in argument, any local covers with jpg or png extension.
        If any, that file will return.'''
    extensions = ['jpg', 'png']            # extensions of files for search
    matches = []                           # files that matches to extensions will save here

    # dir not empty?
    if not os.listdir(dir):
        print 'dir', dir, 'is empty, we will not search any covers in it'
        return False

    # collect all files that match to extensions
    for file in os.listdir(dir):
        for extension in extensions:
            if file.endswith(extension):
                matches.append(dir + '\\' + file)

    # anything matches?
    if not matches:
        print 'dir', dir, 'don\'t have any local covers to artwork'
        return False
    # search well-known names, if find - first matched will be return, if not - first of all will be return
    for file in matches:
        if file[-10:-4].lower() == 'folder':
            return file
        elif file[-9:-4].lower() == 'cover':
            return file
        elif file[-9:-4].lower() == 'front':
            return file
        else:
            print 'dir', dir, 'have some filesm but don\'t have suitable files to artwork, cause filenames not too good for that'
            return False


def isArtworked(au_file):
    '''Check, wouldn't file already been artworked earlier'''
    audiofile = mp3.MP3(au_file, ID3=id3.ID3)
    # for that I love and hate python simultaneously:
    if [items for items in audiofile.keys() if 'APIC' in items]:
        return True
    else:
        return False


def getTags(au_file):
    '''get mp3 file path a argument, parse tags and return id3 Album name and Artist name (or error
    if album or artist name is not found in tags)'''
    audiofile = mp3.MP3(au_file)

    # parse album tag
    try:
        sAlbum = "".join(audiofile.tags['TALB'].text)
        print 'Album is:', sAlbum
    except KeyError:
        print 'Album name in', au_file, 'not found, skipping'
        sAlbum = False

    # parse artist tag
    try:
        sArtist = "".join(audiofile.tags['TPE1'].text)
        print 'Artist is:', sArtist
    except KeyError:
        print 'Artist name in', au_file, 'not found, skipping'
        sArtist = False

    return sArtist, sAlbum


def crLFMRequest((lArtist, lAlbum)):
    '''Build request to send it to lastFM later'''
    data = json.load(open('partwork.conf','r')) # load conffile
    sApiKey  = data['lastFM']['apikey']
    if lArtist and ((lAlbum != 'Single') and (lAlbum != 'single') and lAlbum):
        sArtist = urllib.quote_plus(lArtist.encode('utf-8')) # this done to cyrillic works
        sAlbum  = urllib.quote_plus(lAlbum.encode('utf-8')) # this done to cyrillic works
        params  = {'method' : 'album.getinfo', 'api_key' : sApiKey, 'artist' : sArtist, 'album' : sAlbum}
        return urllib.unquote(urllib.urlencode(params))
    elif lArtist:
        sArtist = urllib.quote_plus(lArtist.encode('utf-8')) # this done to cyrillic works
        params  = {'method' : 'artist.getinfo', 'artist' : sArtist, 'api_key' : sApiKey}
        return urllib.unquote(urllib.urlencode(params))
    else:
        return False


def crLFMQuery(LFMRequest):
    '''Build query to requests. Split from request cause one query may treat
        many requests.'''
    if LFMRequest:
        LFMUrl = 'ws.audioscrobbler.com'
        cConn = httplib.HTTPConnection(LFMUrl)
        cConn.request('GET', '/2.0/?' + LFMRequest)
        cResult = cConn.getresponse()
        cConn.close()
        return cResult.read()
    else:
        return False


def parseImgURL(query, iSize):
    '''Parse query and cut URLs with images from it.'''
    if query:
        bsSoup = bs4.BeautifulSoup(query, features='xml')
        if bsSoup and not bsSoup.find('error', code=6):
            print 'image URL is: ', bsSoup.find('image', size='large').text
            return bsSoup.find('image', size=iSize).text
        else:
            print 'We cannot find suitable artwork URL for that song, sorry'
            return False
    else:
        return False


def getartwork(urlSource):
    '''Get URL with image as parameter and check it. If URL is False,
       then return False. If URL is not false, then create temporary
       file, write content of URL to that file and return full-path
       to that file'''
    if urlSource:
        fSource = urllib.urlopen(urlSource)
        fTarget = tempfile.NamedTemporaryFile(delete=False)
        sData = fSource.read()
        fTarget.write(sData)
        fTarget.close()
        fSource.close()
        return fTarget.name
    else:
        print "Image for this album not found"
        return False


def setartwork(au_file, cover_file):
    '''Setting image inside file.'''
    audiofile = mp3.MP3(au_file, ID3=id3.ID3)
    # As I said previously, for that I love and hate python simultaneously:
    if not [items for items in audiofile.keys() if 'APIC' in items]:
        audiofile.tags.add(
            id3.APIC(
                encoding=3,
                mime='image/jpg',
                type=3,
                desc=u'Cover',
                data=open(cover_file, 'rb').read()
                ))
        audiofile.save()
    else:
        print 'file already have artwork, no need to add another one'

if __name__ == "__main__":
    getmp3()
    # TODO: optionally, we can save downloaded artwork in local directory (but we need to smart save - e.g.
    # do not save cover in directory with many files from different albums)
    # TODO: we can do 'smart' find - e.g. if files from one album locate in one directory, then we don't need to find
    # picture for them many times - only first time is enough
    # TODO: add new search engines
    # TODO: print list of not artworked files after doing all work
    # ---------------------------------------
    # TODO: test on linux?
    # TODO: some refactoring?