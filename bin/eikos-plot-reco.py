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

def DivideByBinWidth( h ):
  nbins = h.GetNbinsX()
  for i in range(nbins):
     bw = h.GetBinWidth(i+1)
     y  = h.GetBinContent(i+1)
     dy = h.GetBinError(i+1)
     h.SetBinContent(i+1, y/bw )
     h.SetBinError(i+1, dy/bw )

#########################################################

infilename = sys.argv[1]
infile = TFile.Open( infilename )

#obs = infilename.split('/')[-1].split('.')[0]

h_data       = infile.Get("data")
h_prediction = infile.Get("prediction_nominal")
h_bkg        = infile.Get("bkg")

DivideByBinWidth( h_data ) 
DivideByBinWidth( h_prediction )
DivideByBinWidth( h_bkg )

SetTH1FStyle( h_prediction, fillstyle=1001, fillcolor=kRed-9, markersize=0, linewidth=0 )
SetTH1FStyle( h_bkg,        fillstyle=1001, fillcolor=kBlue-7, markersize=0, linewidth=0 )

h_unc = TH1F2TGraph( h_prediction )
SetTH1FStyle( h_unc, fillstyle=3354, fillcolor=kGray+3, markersize=0, linewidth=0 )

c = TCanvas("c", "C", 800, 800 )

h_prediction.SetMaximum( 1.3*h_prediction.GetMaximum() )
h_prediction.Draw("h")
h_bkg.Draw("h same")
h_unc.Draw("e2 same")
h_data.Draw("p e same")

h_prediction.GetXaxis().SetTitle( "X" ) #xtitle[obs] )
h_prediction.GetYaxis().SetTitle( "Events / bw ")

lparams = {
        'xoffset' : 0.55,
        'yoffset' : 0.90,
        'width'   : 0.35,
        'height'  : 0.04,
        }

leg = MakeLegend( lparams )
leg.SetTextFont( 42 )
leg.SetNColumns(1)
leg.AddEntry( h_data, "Pseudo-Data", "ep" )
leg.AddEntry( h_prediction, "Signal", "f" )
leg.AddEntry( h_bkg, "Background", "f" )
leg.AddEntry( h_unc, "Stat. Unc.", "f" )
leg.Draw()
leg.SetY1( leg.GetY1() - lparams['height'] * leg.GetNRows() )


gPad.RedrawAxis()

c.SaveAs( "output/img/reco.pdf" )
