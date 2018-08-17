#!/usr/bin/env python

import os, sys
import argparse 
import xml.etree.ElementTree as ET

GeV = 1000.
iLumi = 36.1

from PlottingToolkit import *

from ROOT import *

gROOT.Macro( "rootlogon.C" ) 
gROOT.LoadMacro( "AtlasUtils.C" ) 
gROOT.SetBatch(1)

gStyle.SetErrorX(0)

xtitle = {
"x"       : "X",
"inclusive" : "Inclusive cross-section [pb]",
"t1_pt"   : "p_{T}^{t,1} [GeV]",
"t1_y"    : "|y^{t,1}|",
"t2_pt"   : "p_{T}^{t,2} [GeV]",
"t2_y"    : "|y^{t,2}|",
"tt_m"     : "m^{t#bar{t}} [TeV]", 
"tt_pt"    : "p_{T}^{t#bar{t}} [GeV]", 
"tt_y"     : "|y^{t#bar{t}}|", 
"tt_yB"  : "y_{B}",
"tt_chi"     : "#chi",
"tt_Pout"    : "|p_{out}| [GeV]",
"tt_dPhi" : "#Delta #phi(t_{1}, t_{2})",
"tt_HT"     : "H_{T}^{t#bar{t}} [GeV]",
"tt_cosThS" : "|cos#theta^{*}|",
}

#########################################################

def MakeLegend( params ):
    leg = TLegend( params['xoffset'], params['yoffset'], params['xoffset'] + params['width'], params['yoffset'] )
    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(72)
    leg.SetTextSize(0.04)#0.05)
    return leg


#########################################################


def SetTH1FStyle( h, color = kBlack, linewidth = 1, linestyle=1, fillcolor = 0, fillstyle = 0, markerstyle = 21, markersize = 1.3, fill_alpha=0.0 ):
    '''Set the style with a long list of parameters'''
    
    h.SetLineColor( color )
    h.SetLineWidth( linewidth )
    h.SetFillColor( fillcolor )
    h.SetFillStyle( fillstyle )
    h.SetLineStyle( linestyle )
    h.SetMarkerStyle( markerstyle )
    h.SetMarkerColor( h.GetLineColor() )
    h.SetMarkerSize( markersize )
    if fill_alpha > 0:
       h.SetFillColorAlpha( color, fill_alpha )


#########################################################

def TH1F2TGraph(h):
  g = TGraphErrors()
  g.SetName( "g_%s" % h.GetName() )

  Nbins = h.GetNbinsX()
  for i in range(Nbins):
    x = h.GetBinCenter( i+1 )
    y = h.GetBinContent( i+1 )
    bw = h.GetBinWidth( i+1 )
    dy = h.GetBinError( i+1 )
    dx = bw/2.

    g.SetPoint( i, x, y )
    g.SetPointError( i, dx, dy )

  return g

#########################################################

def DivideBy( h, h_ref ):
  nbins = h_ref.GetNbinsX()
  for i in range(nbins):
     y_ref = h_ref.GetBinContent(i+1)
     y     = h.GetBinContent(i+1)
     dy    = h.GetBinError(i+1)
     h.SetBinContent( i+1, y/y_ref )      
     h.SetBinError( i+1, dy/y_ref )

  return h

#########################################################

test_type = "closure"
if len(sys.argv) > 1: test_type = sys.argv[1]
if not test_type in [ "closure", "stress" ]:
  print "ERROR: unknown type of test:", test_type
  exit(1)

print "INFO: performing a %s test" % test_type

infile_unf = TFile.Open( "output/toymc_statonly_%s/x.toymc.statonly.%s.root" % (test_type,test_type) )
h_unf = infile_unf.Get( "diffxs_statsyst_rel" )

infile_gen = TFile.Open( "toymc.root" )
h_truth_nominal = infile_gen.Get( "truth_nominal_normalized" )
h_truth_other   = infile_gen.Get( "truth_modelling_theta_normalized" )

if test_type == "closure":
  h_truth = h_truth_nominal
else:
  h_truth = h_truth_other
h_ratio = h_unf.Clone("h_ratio")
h_unc   = h_truth.Clone("h_unc")
DivideBy( h_unc, h_truth )
DivideBy( h_ratio, h_truth )

g_unc = TH1F2TGraph( h_unc )
SetTH1FStyle( g_unc, fillstyle=1001, fillcolor=kYellow )
g_unc.SetMinimum(0.8)
g_unc.SetMaximum(1.3)

c = TCanvas("c", "C", 800, 800 )
c.SetRightMargin(0.05)

g_unc.Draw("a e2")

l = TLine()
l.SetLineStyle(kDashed)
l.SetLineWidth(2)
l.SetLineColor(kGray+3)
l.DrawLine(0.,1.,100.,1.)

h_ratio.Draw("p e same") 

g_unc.GetXaxis().SetTitle( "X" )
g_unc.GetYaxis().SetTitle( "Unfolded / Truth" )

txt = TLatex()
txt.SetNDC()
if test_type == "closure":
  txt.DrawLatex( 0.15, 0.85, "Closure test" )
elif test_type == "stress":
  txt.DrawLatex( 0.15, 0.85, "Stress test" )
else:
  pass

gPad.RedrawAxis()

c.SaveAs( "output/img/%s.pdf" % test_type )
