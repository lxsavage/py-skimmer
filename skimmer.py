"""
This script will skim a directory and outputs data about every file inside
(recursively) including:
  * Filename
  * Filepath
  * Last modified date
  * Created date

It is invocated with:
  $ python skimmer.py <input directory> <output file .csv>
"""
import sys, os
from argparse import ArgumentParser
from huepy import *
from halo import Halo
from pandas import DataFrame

S_SKIM = Halo(spinner='dots')
S_SAVE = Halo(spinner='dots')

CLI_ARGS = {
  "INPUT": '',
  "OUTPUT": ''
}

OUTPUT_FORMAT = [ 'Name', 'Path', 'Last modified', 'Created' ]

def processArgs():
  global CLI_ARGS
  parser = ArgumentParser(
    description='Skims a directory and outputs data about every file inside (recursively) to the output file'
  )
  parser.add_argument(
    '-i', '--input',
    dest='inputname',
    help='Input directory path',
    required=True
  )
  parser.add_argument(
    '-o', '--output',
    dest='outputname',
    help='Output file path (has to end in .csv)',
    required=True
  )
  args = parser.parse_args()
  CLI_ARGS["INPUT"] = args.inputname
  CLI_ARGS["OUTPUT"] = args.outputname

def skim():
  global CLI_ARGS
  global OUTPUT_FORMAT
  global S_SKIM
  S_SKIM.start('Starting...')
  out_l = []
  filecount = 0
  for dirname, subdirs, filenames in os.walk(CLI_ARGS["INPUT"]):
    S_SKIM.text = 'Reading directory: {d}'.format(d=dirname)
    for filename in filenames:
      filecount += 1
      stat = os.stat('{d}/{f}'.format(d=dirname, f=filename))
      out_l.append({
        'Name': filename,
        'Path': dirname,
        'Last modified': stat.st_mtime,
        'Created': stat.st_ctime
      })
  S_SKIM.text = 'Compiling...'
  out = DataFrame.from_records([i for i in out_l])
  S_SKIM.stop_and_persist(green('✓'), 'Read directory. Files found: {f}'.format(f=filecount))
  return out[OUTPUT_FORMAT]

def tocsv(df: DataFrame, path: str):
  global S_SAVE
  S_SAVE.start('Saving to {s}'.format(s=path))
  try:
    with open(path, 'w+') as outfile:
      outfile.write(df.to_csv(index=False))
    S_SAVE.stop_and_persist(
      green('✓'),
      'Saved file to {s}'.format(s=path)
    )
  except FileNotFoundError:
    S_SAVE.stop_and_persist(
      red('✗'),
      'Failed to write file. Make sure it isn\'t open in a separate program, such as Excel.'
    )

if __name__ == '__main__':
    processArgs()
    tocsv(skim(), CLI_ARGS["OUTPUT"])
