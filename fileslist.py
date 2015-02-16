import os
import platform
import logging

if platform.system() == 'Windows':
    sep = '\\'
else:
    sep = '/'

def getfiles(file="",directory="",recursive=False):
  # --file processing
  if file:
    files = [' '.join(file)]
    for filename in files:
      # return generator
      yield filename

  # --dir processing
  if directory:
    dirs = [' '.join(directory)]
    if not recursive:
      # return generator
      for file in os.listdir(dirs[0]):
        if file.endswith('.mp3'):
          yield dirs[0]+sep+file
    else:
      logging.debug('Recursive flag enabled')
      for root, dirs, files in os.walk(dirs[0]):
        # return generator
        for file in files:
          if file.endswith('.mp3'):
            yield root+sep+file

if __name__ == '__main__':
  for f in getfiles(directory='.',recursive=True):
      print(f)
