#!/usr/bin/env python

import os, sys

from ROOT import *

lumi = 36074.6

known_observables = [ "t1_pt", "t2_pt", "t1_y", "t2_y", "tt_m", "tt_pt", "tt_y" ]
SRCPATH = "/afs/cern.ch/user/d/disipio/work/public/ttbar_diffxs_13TeV/AnalysisTop/run/output/particle/"

generator  = sys.argv[1]

outfilename = "data/%s.truth.root" % generator
outfile = TFile.Open( outfilename, "RECREATE" )

infilename = SRCPATH + "mc15_13TeV.ttAH_%s.DAOD_TOPQ1.TightTop.particle.nominal.YearAll.histograms.root" % generator
infile = TFile.Open( infilename )

for obs in known_observables:
   hname = "%s_passed_J1_1t1b_J2_1t1b" % ( obs )

   h_gen = infile.Get( hname )
   h_gen.Scale( 1./lumi )

   outfile.cd()
   h_gen.Write( "%s_theory_abs" % obs )

   xs_incl = h_gen.Integral() 
   h_gen.Scale( 1./xs_incl )
   h_gen.Write( "%s_theory_rel" % obs )

infile.Close()
outfile.Close()
