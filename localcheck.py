import os
import logging
from mutagen import id3,mp3

def isFileArtworked(au_file):
  '''Check, wouldn't file already been artworked earlier'''
  audiofile = mp3.MP3(au_file, ID3=id3.ID3)
  # for that I love and hate python simultaneously:
  if [items for items in audiofile.keys() if 'APIC' in items]:
      return True
  else:
      return False


def isLocalCovers(dir):
  ''' Check, is in dir, pass in argument, any local covers with jpg or png extension.
      If any, that file will return.'''
  extensions = ['jpg', 'png']            # extensions of files for search
  matches = []                           # files that matches to extensions will save here

  # dir not empty?
  if not os.listdir(dir):
    logging.info('Dir %s is empty, we will not search any covers in it' % dir)
    return False

  # collect all files that match to extensions
  for file in os.listdir(dir):
    for extension in extensions:
      if file.endswith(extension):
        matches.append(dir + '\\' + file)

  # anything matches?
  if not matches:
    logging.info('Dir %s doesn\'t have any local covers to artwork' % dir)
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
      logging.info('Dir %s have some files but doesn\'t have suitable files to artwork, cause filenames not too good for that' % dir)
      return False
