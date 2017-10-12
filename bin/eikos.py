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
gparams['LUMI']       = 36074.6
gparams['INPUTPATH']  = "$PWD/data/tt_allhad_boosted"

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
     super( EikosPrompt, self ).postloop()

   def do_exit( self, args ):
     BCLog.OutSummary("Bye bye")
     return True
 
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

   def add_sample( self, sname ):
      unfolder.AddSample( sname )
      BCLog.OutSummary( "Added sample %s" % unfolder.GetSample(sname).GetName() )

   #~

   def set_sample_type( self, sname, t ):
      itype = 2
      if t in [ 'data', 'Data' ]: itype = 0
      elif t in [ 'signal', 'Signal' ]: itype = 1
      elif t in [ 'background', "Background", 'bkg', 'Bkg' ]: itype = 2
      elif t in [ 'datadriven', "DataDriven", "dd", "DD" ]: itype = 3
      else: itype = 2

      unfolder.GetSample(sname).SetType( itype )
      if itype == 1: unfolder.SetSignalSample( sname )

      BCLog.OutSummary( "Sample %s: type set to %i (%s)" % ( sname, unfolder.GetSample(sname).GetType(), t )  )

   #~

   def set_sample_latex( self, sname, value ):
      latex = value.replace( '"', '' )
      unfolder.GetSample(sname).SetLatex( latex )
      BCLog.OutSummary(	"Sample %s: latex label = %s" % (sname, value ) )      
   #~

   def unpack_path( self, path, separator=':' ):
      fpath, hpath = path.split(separator)

      fpath = fpath.replace("@INPUTPATH@", gparams['INPUTPATH'] )
      fpath = fpath.replace("@PHSPACE@",   gparams['PHSPACE'] )
      fpath = fpath.replace("@OBS@",       gparams['OBS'] )
      fpath = os.path.expandvars( fpath )

      hpath = hpath.replace("@OBS@",       gparams['OBS'] )
      hpath = hpath.replace("@PHSPACE@",   gparams['PHSPACE'] )   

      return ( fpath, hpath )

   #~

   def set_sample_hpath( self, sname, syst, lvl, path ):
      fpath, hpath = self.unpack_path( path )
      f = TFile.Open( fpath )
      if f.Get( hpath ) == None:
          BCLog.OutSummary( "Sample %s: invalid histogram %s in file %s" % (sname,hpath,fpath) )
          exit(1)
         
      sample = unfolder.GetSample(sname)

      if lvl in [ "reco", "detector" ]: 
            h = TH1D()
            f.Get( hpath ).Copy( h )
#            h.Print("all")     
            sample.SetDetector( h, syst )
            BCLog.OutSummary( "Sample %s: reco histogram %s : %s" %(sname,fpath,hpath) )
      elif lvl in [ "resp", "response" ]:
            h = TH2D()
            f.Get( hpath ).Copy( h ) 
            sample.SetResponse( h, syst )
      elif lvl in [ "gen", "truth", "particle", "parton" ]:
            h = TH1D()
            f.Get( hpath ).Copy( h )
            #ilumi = float( gparams['LUMI'] )
            #h.Scale( 1./ilumi )
            sample.SetTruth( h, syst )
            #BCLog.OutSummary( "Truth histogram is scaled to 1/iLumi" )
            BCLog.OutSummary( "Sample %s: truth histogram %s : %s" %(sname,fpath,hpath) )
      else: 
            BCLog.OutSummary( "Sample %s: invalid level %s" % lvl )
            return False

   ###################

   def add_systematic( self, tokens ):
      sname = tokens[0]
      xmin = -5.0
      xmax =  5.0
      if len(tokens) > 1: xmin = float(tokens[1])
      if len(tokens) > 2: xmax = float(tokens[2])

      unfolder.AddSystematic( sname, xmin, xmax )
      
   ###################

   def set_systematic( self, tokens ):
      pass      

   ###################

   def do_add( self, args ):
      tokens = args.split()
      if len(tokens) < 2: 
        BClog.OutSummary( "Invalid command" )
        return

      what = tokens[0]
      if what == "sample":
         sname = tokens[1]
         self.add_sample( sname )
      elif what == "systematic":
       	 sname = tokens[1]
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
         if value == "path":
            fpath, hpath = self.unpack_path( tokens[2] )
            self.set_data( fpath, hpath )
      elif what == "param":
         pname = tokens[1]
         value = tokens[2]
         self.set_param( pname, value )

      elif what == "sample":
         sname = tokens[1]
         value = tokens[2]
         if value == "path":
            syst = tokens[3]
            lvl  = tokens[4]
            path = tokens[5]
            self.set_sample_hpath( sname, syst, lvl, path )
         elif value == "type":
            self.set_sample_type( sname, tokens[3] )
         elif value == "latex":
            self.set_sample_latex( sname, tokens[3] )

      elif what == "systematic":
         sname = tokens[1]
         param = tokens[2]
         if param == "limits":
            pass
         elif param == "variations":
            var_u = tokens[3]
            var_d = tokens[4]
            unfolder.SetSystematicVariations( sname, var_u, var_d )
 
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
     lumi = float(gparams['LUMI'])
     unfolder.SetLuminosity( lumi )

     unfolder.PrepareForRun()

#     unfolder.SetPrecision( BCEngineMCMC.kMedium )
#     unfolder.SetPrecision( BCEngineMCMC.kHigh )
     unfolder.SetPrecision( int(gparams['PRECISION']) )

     unfolder.PrintSummary()

     unfolder.MarginalizeAll()

     bestfit = unfolder.GetBestFitParameters()
     unfolder.FindMode( bestfit )

     outfile = TFile.Open( "output/diffxs.root", "RECREATE" )

     n = bestfit.size()
     for i in range(n):
       print "%-2i) %f" % ( i, bestfit[i] )

     diffxs_abs = unfolder.GetDiffxsAbs()

     theory_abs = unfolder.GetSignalSample().GetTruth()
     theory_abs.Scale( 1./lumi )

     migrations = unfolder.GetSignalSample().GetMigrations()
     efficiency = unfolder.GetSignalSample().GetEfficiency()
     acceptance = unfolder.GetSignalSample().GetAcceptance()

     diffxs_abs.SetLineColor(kBlack)
     diffxs_abs.SetMarkerColor(kBlack)
     diffxs_abs.SetLineWidth(2)

     theory_abs.SetLineColor(kRed)
     theory_abs.SetMarkerColor(kRed)
     theory_abs.SetLineWidth(2)

     migrations.SetMinimum( 0. )
     migrations.SetMaximum( 1.0 )

     efficiency.SetMinimum( 0. )
     efficiency.SetMaximum( 1.0 )
     efficiency.SetLineColor(kRed)
     efficiency.SetMarkerColor(kRed)
     efficiency.SetLineWidth(2)

     acceptance.SetMinimum( 0. )
     acceptance.SetMaximum( 1.0	)
     acceptance.SetLineColor(kBlue)
     acceptance.SetMarkerColor(kBlue)
     acceptance.SetLineWidth(2)

     data       = unfolder.GetData()
     signal     = unfolder.GetSignalSample().GetDetector()

     prediction = signal.Clone( "prediction" )
     dataminusbkg = data.Clone( "dataminusbkg" )

     isClosureTest = True
     if unfolder.GetBackgroundSample().get() != None: isClosureTest = False 

     if isClosureTest == False:
       BCLog.OutSummary( "Background found: this is a data-bkg unfolding" )
       background = unfolder.GetBackgroundSample().GetDetector()
       prediction.Add( background.get() )
       dataminusbkg.Add( background.get(), -1.0 )
     else:
        BCLog.OutSummary( "No background: this is a closure test" ) 

     data.SetLineColor( kBlack )
     data.SetMarkerColor( kBlack )
     data.SetLineWidth(2)

     prediction.SetLineColor( kGreen+2 )
     prediction.SetMarkerSize(0)
     prediction.SetFillStyle(1001)
     prediction.SetFillColor( kGreen+2 )

     dataminusbkg.SetLineColor(	kRed )
     dataminusbkg.SetMarkerColor( kRed )
     dataminusbkg.SetLineWidth(2)

     closure = diffxs_abs.get().Clone( "closure" )
     closure.Divide( theory_abs.get() )

     closure.SetLineColor( kBlack )
     closure.SetMarkerColor( kBlack )
     closure.SetLineWidth(2)

     outfile.cd()

     data.get().Write( "data" )

     if	isClosureTest == False:
        background.get().Write( "background" )
     signal.get().Write( "signal" )
     prediction.Write( "prediction" )
     dataminusbkg.Write( "dataminusbkg" )
     theory_abs.get().Write( "theory_abs" )
     diffxs_abs.get().Write( "diffxs_abs" )
     migrations.get().Write( "migrations" )
     efficiency.get().Write( "efficiency" )
     acceptance.get().Write( "acceptance" )
     closure.Write( "closure" )

     outfile.Close()

     gROOT.SetBatch(True)

     unfolder.PrintParameterPlot( "output/parameters.pdf" )
     unfolder.PrintCorrelationPlot( "output/correlations.pdf" )
     unfolder.PrintKnowledgeUpdatePlots( "output/update.pdf" )
     unfolder.PrintAllMarginalized( "output/marginalized.pdf" )


##############################

if __name__ == '__main__':
  prompt = EikosPrompt()
  prompt.prompt = 'eikos> '

  if len(sys.argv) > 1:
     cmdfile = sys.argv[1]
     prompt.cmdqueue.extend( file(cmdfile) )

  prompt.cmdloop()
