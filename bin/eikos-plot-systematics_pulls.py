#!/usr/bin/env python

import os, sys
import argparse 

from PlottingToolkit import *

from ROOT import *

gROOT.Macro( "rootlogon.C" ) 
gROOT.LoadMacro( "AtlasUtils.C" ) 

gROOT.SetBatch(1)

infilename = "output/diffxs.root"
if len(sys.argv) > 1:
   infilename = sys.argv[1]
infile = TFile.Open( infilename )

h_pulls = infile.Get( "pulls" )

h_pulls.SetMaximum(  2.5 )
h_pulls.SetMinimum( -2.5 )

n_syst = h_pulls.GetNbinsX()

h_pulls.SetMarkerStyle( 20 )
h_pulls.SetMarkerSize( 1.5 )
h_pulls.GetXaxis().LabelsOption( "v" )
h_pulls.GetXaxis().SetLabelSize(0.03)
h_pulls.GetYaxis().SetTitle( "( #theta_{fit} - #theta_{0} ) / #Delta#theta" );

c = TCanvas( "c", "C", 1200, 800 )
c.SetBottomMargin( 0.50 )

h_pulls.Draw( "e1 p x0" )

box_1s = TH1D( "box_1s", "", 1, h_pulls.GetXaxis().GetXmin(), h_pulls.GetXaxis().GetXmax() )
box_1s.SetBinContent( 1, 0.0 )
box_1s.SetBinError( 1, 1.0 )
box_1s.SetFillStyle( 1001 )
#box_1s.SetFillColor( kGreen )
#box_1s.SetFillStyle( 3354 )
box_1s.SetFillColor( kGray+1 )
box_1s.SetMarkerSize(0)
#box_1s.SetLineWidth(0)

box_2s = TH1D( "box_2s", "", 1, h_pulls.GetXaxis().GetXmin(), h_pulls.GetXaxis().GetXmax() )
box_2s.SetBinContent( 1, 0.0 )
box_2s.SetBinError( 1, 2.0 )
box_2s.SetFillStyle( 3354 )
#box_2s.SetFillStyle( 1001 )
#box_2s.SetFillColor( kYellow )
box_2s.SetFillColor( kGray+2 )
box_2s.SetMarkerSize(0)
#box_2s.SetLineWidth(0)

box_2s.Draw( "e2 same ][" )
box_1s.Draw( "e2 same ][" )

l = TLine()
l.SetLineStyle( kDashed )
l.SetLineColor(kGray+3)
l.SetLineWidth(1)
l.DrawLine( h_pulls.GetXaxis().GetXmin(), 0., h_pulls.GetXaxis().GetXmax(), 0. )
h_pulls.Draw( "e1 p x0 same" )

gPad.RedrawAxis()

c.SaveAs( "output/img/pulls.pdf" )

