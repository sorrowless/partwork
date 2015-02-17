from mutagen import id3,mp3
import urllib.request
import logging

def gettags(au_file):
  '''get mp3 file path a argument, parse tags and return id3 Album name and Artist name (or error
  if album or artist name is not found in tags)'''
  audiofile = mp3.MP3(au_file)

  # parse album tag
  try:
    sAlbum = "".join(audiofile.tags['TALB'].text)
    print('Album is:', sAlbum)
  except (KeyError, TypeError):
    logging.warn('Album name in %s not found' % au_file)
    sAlbum = False

  # parse artist tag
  try:
    sArtist = "".join(audiofile.tags['TPE1'].text)
    print('Artist is:', sArtist)
  except (KeyError, TypeError):
    logging.warn('Artist name in %s not found' % au_file)
    sArtist = False

  return sArtist,sAlbum


def getartwork(urlSource):
  '''Get URL with image as parameter and check it. If URL is False,
     then return False. If URL is not false, then create temporary
     file, write content of URL to that file and return full-path
     to that file'''
  if urlSource:
    fSource = urllib.request.urlopen(urlSource)
    fTarget = tempfile.NamedTemporaryFile(delete=False)
    sData = fSource.read()
    fTarget.write(sData)
    fTarget.close()
    fSource.close()
    return fTarget.name
  else:
    logging.warn("Image for this file not found\n")
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
        desc='Cover',
        data=open(cover_file, 'rb').read()
        ))
    audiofile.save()
  else:
      print('file already have artwork, no need to add another one')

