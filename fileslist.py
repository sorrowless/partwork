import sys
import os
import argparse
import platform

if platform.system() == 'Windows':
    sep = '\\'
else:
    sep = '/'

def createParser():
  '''Create parser for command-line arguments'''
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--file', nargs = '+')
  parser.add_argument('-d', '--dir', nargs = '+')
  parser.add_argument('-r', '--recursive', action = 'store_true')
  return parser

def getfiles():
  parser = createParser()
  namespace = parser.parse_args(sys.argv[1:])

  # namespaces parsing processed splitly.
  # --file processing
  if namespace.file:
    files = [' '.join(namespace.file)]
    for filename in files:
      # return generator
      yield filename

  # --dir processing
  if namespace.dir:
    dirs = [' '.join(namespace.dir)]
    if not namespace.recursive:
      # return generator
      for file in os.listdir(dirs[0]):
        if file.endswith('.mp3'):
          yield dirs[0]+sep+file
    else:
      print('Recursive flag enabled')
      for root, dirs, files in os.walk(dirs[0]):
        # return generator
        for file in files:
          if file.endswith('.mp3'):
            yield root+sep+file

if __name__ == '__main__':
  for f in getfiles():
      print(f)
