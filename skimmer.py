"""This script will skim a directory and outputs data about every file inside
(recursively) including:
  * Filename
  * Filepath
  * Last modified date
  * Created date

It is invocated with:
  $ python skimmer.py <input directory> <output file .csv>
"""
import sys, os, re
from argparse import ArgumentParser

# External dependencies
from huepy import *
from halo import Halo
from pandas import DataFrame

S_SKIM = Halo(spinner='dots')
S_SAVE = Halo(spinner='dots')

CLI_ARGS = {
  "INPUT": '',
  "OUTPUT": ''
}

OUTPUT_FORMAT = [ 'Name', 'Path', 'Size', 'Last modified (TS)', 'Created (TS)' ]

def processArgs():
  """Proccesses the command line arguments and adds them to the CLI_ARGS dictionary
  """
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

def convertToSize(bytes: int):
  """Converts the bytes to the appropriate unit for its simplest representation
  
  Arguments:
      bytes {int} -- The amount of bytes to be converted to an appropriate unit
  
  Returns:
      str -- A formatted, easily readable data approximation for the bytes
  """
  BYTE_REPRESENTATION = {
    "TiB": int(1.20892582E+24),
    "GiB": int(1.099511628E+12),
    "MiB": 1048576,
    "KiB": 1024
  }

  output = ""
  for item in BYTE_REPRESENTATION:
    if bytes >= BYTE_REPRESENTATION[item]:
      value = round((float(bytes) / BYTE_REPRESENTATION[item]) * 100) / 100 # Round to 2 decimal places
      output = "{b} {u}".format(b=value,u=item)
      break
  
  if output == "":
    output = "{b} bytes".format(b=bytes)

  return output

def skim():
  """Skims over the given directory to get the data for exporting
  
  Returns:
      DataFrame -- Data to be exported to a CSV
  """
  global CLI_ARGS
  global OUTPUT_FORMAT
  global S_SKIM
  S_SKIM.start('Starting...')
  out_l = []
  filecount = 0
  size=0
  for dirname, subdirs, filenames in os.walk(CLI_ARGS["INPUT"]):
    S_SKIM.text = 'Reading directory: {d}'.format(d=dirname)
    for filename in filenames:
      filecount += 1
      try:
        stat = os.stat('{d}/{f}'.format(d=dirname, f=filename)) # Get the path to the file
        size += stat.st_size
        out_l.append({
          'Name': filename,
          'Path': dirname,
          'Size': convertToSize(stat.st_size),
          'Last modified (TS)': stat.st_mtime,
          'Created (TS)': stat.st_ctime
        })
      except FileNotFoundError:
        out_l.append({
          'Name': filename,
          'Path': dirname,
          'Size': convertToSize(float(-1)),
          'Last modified (TS)': float(-1),
          'Created (TS)': float(-1)
        })
  S_SKIM.text = 'Compiling...'
  out = DataFrame.from_records([i for i in out_l])

  S_SKIM.stop_and_persist(
    green('✓'),
    'Read directory. Size: {s}. Files found: {f}'.format(s=convertToSize(size),f=filecount)
  )

  return out[OUTPUT_FORMAT]

def tocsv(df: DataFrame, path: str):
  """Converts a DataFrame to a CSV file, then saves it
  
  Arguments:
      df {DataFrame} -- The input data
      path {str} -- The path to save the CSV; this will throw an error if the path's file is locked
  """
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
