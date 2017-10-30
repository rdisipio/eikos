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

gROOT.ProcessLine("gErrorIgnoreLevel = kSysError;")
gROOT.SetBatch(True)

unfolder = EikosUnfolder()

gparams = {}
# set some default
gparams['ACCURACY']   = 'low'
gparams['PHSPACE']    = "particle"
gparams['OBS']        = "t1_pt"
gparams['LUMI']       = 36074.6
gparams['INPUTPATH']  = "$PWD/data/tt_allhad_boosted"
gparams['REGULARIZATION'] = 1
gparams['OUTPUTPATH'] = "$PWD/output"
gparams['OUTPUTTAG'] = "statonly"

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
     BCLog.OutSummary("Welcome to Eikos v0.1, eh!")

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
            hname = "reco_%s" % ( syst )
            sample.SetDetector( h, syst, hname )
#            BCLog.OutSummary( "Sample %s: reco histogram %s : %s" %(sname,fpath,hpath) )
      elif lvl in [ "resp", "response" ]:
            h = TH2D()
            f.Get( hpath ).Copy( h ) 
            hname = "resp_%s" % ( syst )
            sample.SetResponse( h, syst, hname )
      elif lvl in [ "gen", "truth", "particle", "parton" ]:
            h = TH1D()
            f.Get( hpath ).Copy( h )
            hname = "truth_%s" % ( syst )
            sample.SetTruth( h, syst, hname )
            #BCLog.OutSummary( "Truth histogram is scaled to 1/iLumi" )
#            BCLog.OutSummary( "Sample %s: syst %s :: truth histogram %s : %s" %(sname,syst,fpath,hpath) )
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
            var_d = "@symmetrize@"
            if len(tokens)>4:  var_d = tokens[4]

            unfolder.SetSystematicVariations( sname, var_u, var_d )
         elif param  == "type":
            type = tokens[3]
            if type in [ "detector" ]: 
               unfolder.SetSystematicType( sname, 0 )
            elif type in [ "modelling", "generator" ]: 
               unfolder.SetSystematicType( sname, 1 )
            else:
               print "ERROR: unknown type of systematic", type
               exit(1)  

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
     loaded_RooUnfold = gSystem.Load("libRooUnfold.so")
     if not loaded_RooUnfold == 0:
        print "INFO: RooUnfold not found."
     else:
        print "INFO: RooUnfold found. Output file will contain unfolded distributions with (unregularized) Matrix Inversion and (regularized) Iterative Bayesian with Nitr=4"

     # create output directory
     gparams['OUTPUTPATH'] = os.path.expandvars( gparams['OUTPUTPATH'] ) + "/" + gparams['OUTPUTTAG'] + "/"
     if not os.path.exists( gparams['OUTPUTPATH'] ):
        os.makedirs( gparams['OUTPUTPATH'] )
     BCLog.OutSummary( "Output path: %s" % gparams['OUTPUTPATH'] )     

     lumi = float(gparams['LUMI'])
     unfolder.SetLuminosity( lumi )

     unfolder.SetPrecision( int(gparams['PRECISION']) )
     if int(gparams['PRECISION']) == 2:
       unfolder.SetNChains( 5 )
       unfolder.SetNIterationsPreRunMax( 200000 )
       unfolder.SetNIterationsRun( 200000 )
       unfolder.SetNIterationsPreRunCheck( 1000 )

     BCLog.OutSummary( "\033[92m\033[1mFirst run: estimating prior distribution...\033[0m" )
     run_stage = kStageEstimatePrior
     unfolder.SetRegularization( 0 ) # start with unregularized
     unfolder.PrepareForRun( run_stage )
     unfolder.MarginalizeAll()
     bestfit = unfolder.GetBestFitParameters()
     unfolder.FindMode( bestfit )
     unfolder.PrintSummary()
     BCLog.OutSummary( "\033[92m\033[1mEnd of first run: prior distribution estimated.\033[0m" )
 
     unfolder.PrintKnowledgeUpdatePlots( "%s/%s_update_prior.pdf"  % ( gparams['OUTPUTPATH'], gparams['OBS'] ) )
     unfolder.PrintAllMarginalized( "%s/%s_marginalized_prior.pdf" % ( gparams['OUTPUTPATH'], gparams['OBS'] ) )

     # Store prior for 2nd run stage
     prior_abs = unfolder.GetDiffxsAbs()
     xs_incl_prior = prior_abs.Integral()
     prior_rel = prior_abs.Clone( "prior_rel" )
     prior_rel.Scale( 1./xs_incl_prior )

     BCLog.OutSummary( "\033[92m\033[1mStarting stat+syst run.\033[0m" )
     run_stage = kStageStatSyst
     unfolder.SetPrior( prior_abs )
     unfolder.SetRegularization( int(gparams['REGULARIZATION']) )
     unfolder.PrepareForRun( run_stage )
     unfolder.MarginalizeAll()
     bestfit = unfolder.GetBestFitParameters()
     unfolder.FindMode( bestfit )
     unfolder.PrintSummary()
     BCLog.OutSummary( "\033[92m\033[1mEnd of second run: posterior distributions with stat+syst uncertainties estimated.\033[0m" )

     unfolder.PrintKnowledgeUpdatePlots( "%s/%s_update_statsyst.pdf"  % ( gparams['OUTPUTPATH'], gparams['OBS'] ) )
     unfolder.PrintAllMarginalized( "%s/%s_marginalized_statsyst.pdf" % ( gparams['OUTPUTPATH'], gparams['OBS'] ) )
#     unfolder.PrintCorrelationPlot( "%s/%s_correlations.pdf" % ( gparams['OUTPUTPATH'], gparams['OBS'] ) )
#     unfolder.PrintParameterPlot( "%s/%s_parameters.pdf"     % ( gparams['OUTPUTPATH'], gparams['OBS'] ) )

     outfilename = "%s/%s.diffxs.root" % ( gparams['OUTPUTPATH'], gparams['OBS'] )
     outfile = TFile.Open( outfilename, "RECREATE" )

     n = bestfit.size()
     for i in range(n):
       print "%-2i) %f" % ( i, bestfit[i] )

     migrations = unfolder.GetSignalSample().GetMigrations()
     efficiency = unfolder.GetSignalSample().GetEfficiency()
     acceptance = unfolder.GetSignalSample().GetAcceptance()

     diffxs_abs = unfolder.GetDiffxsAbs()
     diffxs_abs.SetLineColor(kBlack)
     diffxs_abs.SetMarkerColor(kBlack)
     diffxs_abs.SetLineWidth(2)

     diffxs_rel = unfolder.GetDiffxsRel()
     diffxs_rel.SetLineColor(kBlack)
     diffxs_rel.SetMarkerColor(kBlack)
     diffxs_rel.SetLineWidth(2)

     theory_abs = unfolder.GetSignalSample().GetTruth()
     theory_abs.Scale( 1./lumi )
     theory_abs.SetLineColor(kRed)
     theory_abs.SetMarkerColor(kRed)
     theory_abs.SetLineWidth(2)

     xs_incl_theory = theory_abs.Integral()

     theory_rel = theory_abs.Clone( "theory_rel" )
     theory_rel.Scale( 1./xs_incl_theory )
     theory_rel.SetLineColor(kRed)
     theory_rel.SetMarkerColor(kRed)
     theory_rel.SetLineWidth(2)

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

     xs_incl = unfolder.GetMarginalizedHistogram( "xs_incl" )

     pulls = unfolder.GetSystematicsPullHistogram();

     diffxs_ib_abs = None
     diffxs_ib_rel = None
     diffxs_mi_abs = None
     diffxs_mi_rel = None
     if loaded_RooUnfold == 0:
        h_psig = dataminusbkg.Clone( "pseudosignal" )
        h_psig.Multiply( acceptance.get() )

        h_response = unfolder.GetSignalSample().GetResponse().get()
        m_response = RooUnfoldResponse( 0, 0, h_response, h_response.GetName(), h_response.GetTitle() )
        m_response.UseOverflow( False )

        unfolder_ib = RooUnfoldBayes( "IB", "Iterative Baysian" )
        unfolder_ib.SetIterations( 4 )   
        unfolder_ib.SetVerbose( 0 )
        unfolder_ib.SetSmoothing( 0 )

        unfolder_ib.SetResponse( m_response ) 
        unfolder_ib.SetMeasured( h_psig ) 
 
        diffxs_ib_abs = unfolder_ib.Hreco() # RooUnfold.kNoError ) 
        diffxs_ib_abs.SetName( "diffxs_IB_abs" )
        diffxs_ib_abs.Divide( efficiency.get() )
        diffxs_ib_abs.Scale( 1./lumi )
        diffxs_ib_abs.SetLineColor(kGreen+3)
        diffxs_ib_abs.SetLineWidth(2)
        diffxs_ib_abs.SetMarkerColor(kGreen+3)

        xs_incl_ib = diffxs_ib_abs.Integral()
        diffxs_ib_rel = diffxs_ib_abs.Clone( "diffxs_IB_rel" )
        diffxs_ib_rel.Scale( 1./xs_incl_ib )

        unfolder_ib.Reset()

        unfolder_mi = RooUnfoldInvert( "MI", "Matrix Inversion" )
        unfolder_mi.SetVerbose( 0 )

        unfolder_mi.SetResponse( m_response )
        unfolder_mi.SetMeasured( h_psig )

        diffxs_mi_abs = unfolder_mi.Hreco() # RooUnfold.kNoError )
        diffxs_mi_abs.SetName( "diffxs_MI_abs" )
        diffxs_mi_abs.Divide( efficiency.get() )
        diffxs_mi_abs.Scale( 1./lumi )
        diffxs_mi_abs.SetLineColor(kBlue)
        diffxs_mi_abs.SetLineWidth(2)
        diffxs_mi_abs.SetMarkerColor(kBlue)

        xs_incl_mi = diffxs_mi_abs.Integral()
        diffxs_mi_rel = diffxs_mi_abs.Clone( "diffxs_MI_rel" )
        diffxs_mi_rel.Scale( 1./xs_incl_mi )

        unfolder_mi.Reset()


     outfile.cd()

     data.get().Write( "data" )

     if	isClosureTest == False:
        background.get().Write( "background" )

     signal.get().Write( "signal" )
     prediction.Write( "prediction" )
     dataminusbkg.Write( "dataminusbkg" )

     migrations.get().Write( "migrations" )
     efficiency.get().Write( "efficiency" )
     acceptance.get().Write( "acceptance" )

     theory_abs.get().Write( "theory_abs" )
     prior_abs.get().Write( "prior_abs" )
     diffxs_abs.get().Write( "diffxs_abs" )

     theory_rel.Write( "theory_rel" )
     prior_rel.Write( "prior_rel" )
     diffxs_rel.get().Write( "diffxs_rel" )

     closure.Write( "closure" )
     xs_incl.Write( "xs_incl" )

     pulls.get().Write( "pulls" )

     if loaded_RooUnfold == 0:
       diffxs_mi_abs.Write( "diffxs_MI_abs" )
       diffxs_mi_rel.Write( "diffxs_MI_rel" ) 

       diffxs_ib_abs.Write( "diffxs_IB_abs" )
       diffxs_ib_rel.Write( "diffxs_IB_rel" ) 

     # Final statistics 
     BCLog.OutSummary( "\033[92m\033[1mFinal statistics:\033[0m" ) 
     BCLog.OutSummary( "\033[92m\033[1mNB: covariance matrix not implemented yet\033[0m" ) 

     NDF_abs = theory_abs.GetNbinsX()
     NDF_rel = NDF_abs - 1 

     chi2_prior_vs_theory_abs  = prior_abs.Chi2Test(  theory_abs.get(), "WW CHI2" ) 
     chi2_diffxs_vs_theory_abs = diffxs_abs.Chi2Test( theory_abs.get(), "WW CHI2" )
     chi2_diffxs_vs_prior_abs  = diffxs_abs.Chi2Test( prior_abs.get(),  "WW CHI2" )

     chi2_prior_vs_theory_rel  = prior_rel.Chi2Test(  theory_rel, "WW CHI2" )
     chi2_diffxs_vs_theory_rel = diffxs_rel.Chi2Test( theory_rel, "WW CHI2" )
     chi2_diffxs_vs_prior_rel  = diffxs_rel.Chi2Test( prior_rel,  "WW CHI2" )

     pvalue_prior_vs_theory_abs  = TMath.Prob( chi2_prior_vs_theory_abs,  NDF_abs )
     pvalue_diffxs_vs_theory_abs = TMath.Prob( chi2_diffxs_vs_theory_abs, NDF_abs ) 
     pvalue_diffxs_vs_prior_abs  = TMath.Prob( chi2_diffxs_vs_prior_abs,  NDF_abs )

     pvalue_prior_vs_theory_rel  = TMath.Prob( chi2_prior_vs_theory_rel,  NDF_rel )
     pvalue_diffxs_vs_theory_rel = TMath.Prob( chi2_diffxs_vs_theory_rel, NDF_rel )
     pvalue_diffxs_vs_prior_rel  = TMath.Prob( chi2_diffxs_vs_prior_rel,  NDF_rel )
     
     BCLog.OutSummary( "[prior,  theory] :: abs :: chi2/NDF = %.2f/%i = %.2f :: pvalue = %.3f" % ( chi2_prior_vs_theory_abs,  NDF_abs, chi2_prior_vs_theory_abs/NDF_abs,  pvalue_prior_vs_theory_abs  ) )
     BCLog.OutSummary( "[diffxs, theory] :: abs :: chi2/NDF = %.2f/%i = %.2f :: pvalue = %.3f" % ( chi2_diffxs_vs_theory_abs, NDF_abs, chi2_diffxs_vs_theory_abs/NDF_abs, pvalue_diffxs_vs_theory_abs ) )
     BCLog.OutSummary( "[diffxs, prior ] :: abs :: chi2/NDF = %.2f/%i = %.2f :: pvalue = %.3f" % ( chi2_diffxs_vs_prior_abs,  NDF_abs, chi2_diffxs_vs_prior_abs/NDF_abs,  pvalue_diffxs_vs_prior_abs ) )
     BCLog.OutSummary( "[prior,  theory] :: rel :: chi2/NDF = %.2f/%i = %.2f :: pvalue = %.3f" % ( chi2_prior_vs_theory_rel,  NDF_rel, chi2_prior_vs_theory_rel/NDF_rel,  pvalue_prior_vs_theory_rel  ) )
     BCLog.OutSummary( "[diffxs, theory] :: rel :: chi2/NDF = %.2f/%i = %.2f :: pvalue = %.3f" % ( chi2_diffxs_vs_theory_rel, NDF_rel, chi2_diffxs_vs_theory_rel/NDF_rel, pvalue_diffxs_vs_theory_rel ) )
     BCLog.OutSummary( "[diffxs, prior ] :: rel :: chi2/NDF = %.2f/%i = %.2f :: pvalue = %.3f" % ( chi2_diffxs_vs_prior_rel,  NDF_rel, chi2_diffxs_vs_prior_rel/NDF_rel,  pvalue_diffxs_vs_prior_rel ) )

     if pvalue_prior_vs_theory_abs  < 0.05: BCLog.OutSummary( "Prior  (abs) incompatible with theory model" )
     if pvalue_diffxs_vs_theory_abs < 0.05: BCLog.OutSummary( "Diffxs (abs) incompatible with theory model" )
     if pvalue_diffxs_vs_prior_abs  < 0.05: BCLog.OutSummary( "Diffxs (abs) incompatible with prior" )
     if	pvalue_prior_vs_theory_rel  < 0.05: BCLog.OutSummary( "Prior  (rel) incompatible with theory model" )
     if	pvalue_diffxs_vs_theory_rel < 0.05: BCLog.OutSummary( "Diffxs (rel) incompatible with theory model" )
     if	pvalue_diffxs_vs_prior_rel  < 0.05: BCLog.OutSummary( "Diffxs (rel) incompatible with prior" )

     outfile.Close()
     BCLog.OutSummary( "Output file created: %s" % outfile.GetName() )


##############################

if __name__ == '__main__':
  prompt = EikosPrompt()
  prompt.prompt = 'eikos> '

  if len(sys.argv) > 1:
     cmdfile = sys.argv[1]
     prompt.cmdqueue.extend( file(cmdfile) )

  prompt.cmdloop()
