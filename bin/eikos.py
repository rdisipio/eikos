#!/usr/bin/env python

import os, sys

import fileinput

from array import array
import argparse
from cmd import Cmd

from ROOT import *

gSystem.Load( "libBAT.so")
gSystem.Load( "libEikos.so" )

from ROOT import *

unfolder = EikosUnfolder()

gparams = {}
# set some default
gparams['ACCURACY']   = 'low'
gparams['PHSPACE']    = "particle"
gparams['OBS']        = "t1_pt"
gparams['ILUMI']      = 36074.6
gparams['INPUTPATH']  = "$PWD/data/tt_allhad_boosted"

class SampleWrapper( object ):
   def __init__(self):
      self.name = ""
      
samples = {}

systematics = {}

BCLog.OpenLog("log.txt")
BCLog.SetLogLevel(BCLog.detail)

##############################


class EikosPrompt( Cmd, object ):

   def __init__(self):
     super( EikosPrompt, self ).__init__()

   def do_EOF(self, line):
     return True

   def preloop( self ):
     BCLog.OutSummary("Welcome to Eikos v2.0, eh!")

     self.print_params()
     super( EikosPrompt, self ).preloop()

   def emptyline(self):
     pass

   def postloop( self ):
     BCLog.OutSummary("Bye bye")
     super( EikosPrompt, self ).postloop()
 
   #~~~~~~~~~~~~~~~~~~~~~~~

   def set_param( self, key, value ):
      gparams[key] = value
      value = os.path.expandvars( value )
      BCLog.OutSummary("Global parameter: %-15s = %s" % (key,value) )

   def get_param( self, k ):
      return gparams[k]

   def print_param( self, k ):
      v = self.get_param( k )
      BCLog.OutSummary("%-15s = %s" % ( k, v ) )

   def print_params( self ):
      BCLog.OutSummary("Defined global parameters:")
      keys = gparams.keys()
      keys.sort()
      for k in keys:
         self.print_param( k )

   #~~~~~~~~~~~~~~~~~~~~~~~~

   def set_data( self, fpath, hpath ):
      fpath = fpath.replace("@INPUTPATH@", gparams['INPUTPATH'] )
      fpath = fpath.replace("@PHSPACE@",   gparams['PHSPACE'] )
      fpath = fpath.replace("@OBS@",       gparams['OBS'] )
      fpath = os.path.expandvars( fpath )

      hpath = hpath.replace("@OBS@",       gparams['OBS'] )
      hpath = hpath.replace("@PHSPACE@",   gparams['PHSPACE'] )   

      f = TFile.Open( fpath )
      h = f.Get( hpath )
      if h == None:
         BCLog.OutSummary("Invalid histogram %s in file %s" % ( hpath, fpath ) )
      else:
         BCLog.OutSummary("Data file:      %s" % fpath )
         BCLog.OutSummary("Data histogram: %s" % hpath )

      unfolder.SetData( h )

      f.Close()

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~

   def add_sample( self, tokens ):
      sname = tokens[0]
      samples[sname] = SampleWrapper()
      samples[sname].name = sname

      unfolder.AddSample( sname )
      BCLog.OutSummary( "Added sample %s" % sname )
   #~

   def set_sample_type( self, sname, t ):
      itype = 1
      if t in [ 'data', 'Data' ]: itype = 0
      elif t in [ 'signal', 'Signal' ]: itype = 1
      elif t in [ 'background', "Background", 'bkg', 'Bkg' ]: itype = 2
      elif t in [ 'datadriven', "DataDriven", "dd", "DD" ]: itype = 3
      else: itype = 1

      samples[sname].type = itype
      unfolder.GetSample(sname).SetType( itype )
      BCLog.OutSummary( "Sample %s: type set to %i (%s)" % ( sname, unfolder.GetSample(sname).GetType(), t )  )

   #~

   def set_sample_latex( self, sname, value ):
      latex = value.replace( '"', '' )
      unfolder.GetSample(sname).SetLatex( latex )
      BCLog.OutSummary(	"Sample %s: latex label = %s" % (sname, value ) )      
   #~

   ###################

   def add_systematic( self, tokens ):
      sname = tokens[0]
      xmin = -5.0
      if len(tokens) > 1: xmin = float(tokens[1])
      xmax =  5.0
      if len(tokens) > 2: xmax = float(tokens[2])

      unfolder.AddSystematic( sname, xmin, xmax )
      

   ###################

   def do_add( self, args ):
      tokens = args.split()
      if len(tokens) < 2: 
        BClog.OutSummary( "Invalid command" )
        return

      what = tokens[0]
      if what == "sample":
         self.add_sample( tokens[1:] )
      elif what == "systematic":
         self.add_systematic( tokens[1:] )

   ###################

   def do_set( self, args ):
      tokens = args.split()
      if len(tokens) < 2:
        BClog.OutSummary( "Invalid command" )
        return

      what = tokens[0]
      if what == "data":
         value = tokens[1]
         if value == "hpath":
            fpath, hpath = tokens[2].split(':')
            self.set_data( fpath, hpath )
      elif what == "param":
         pname = tokens[1]
         value = tokens[2]
         self.set_param( pname, value )

      elif what == "sample":
         sname = tokens[1]
         value = tokens[2]
         if value == "hpath": #TODO
            fpath, hpath = tokens[3].split(':')
            self.set_sample_hpath( sname, fpath, hpath )
         elif value == "type":
            self.set_sample_type( sname, tokens[3] )
         elif value == "latex":
            self.set_sample_latex( sname, tokens[3] )

   ###################

   def do_get( self, args ):
      tokens = args.split()
      if len(tokens) < 2:
        BClog.OutSummary( "Invalid command" )
        return
      what = tokens[0]
      if what == "param":
         pname = tokens[1]
         self.get_param( pname )

   ###################

   def do_print( self, args ):
      tokens = args.split()
      if len(tokens) < 2:
        BClog.OutSummary( "Invalid command" )
        return

      what = tokens[0]
      if what == "params":
         self.print_params()
      elif what == "param":
         self.print_param( tokens[1] )

   ###################

   def do_run( self, args ):
     unfolder.PrintSummary()


##############################

if __name__ == '__main__':
  prompt = EikosPrompt()
  prompt.prompt = 'eikos> '

  if len(sys.argv) > 1:
     cmdfile = sys.argv[1]
     prompt.cmdqueue.extend( file(cmdfile) )

  prompt.cmdloop()
