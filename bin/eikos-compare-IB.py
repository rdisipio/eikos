#!/usr/bin/env python

import os,sys
from ROOT import *

gROOT.Macro( "rootlogon.C" )
gROOT.LoadMacro( "AtlasUtils.C" )

gROOT.SetBatch(1)

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

    g.SetPoint( i, x, y )
    g.SetPointError( i, bw/2, dy )

  return g

#########################################################

infilename = sys.argv[1]
infile = TFile.Open( infilename )

obs = infilename.split('/')[-1].split('.')[0]

h_eikos = infile.Get( "diffxs_statsyst_rel" )
h_IB    = infile.Get( "diffxs_IB_rel" )
h_MI    = infile.Get( "diffxs_MI_rel" )

h_IB.Divide( h_eikos )
h_MI.Divide( h_eikos )

SetTH1FStyle( h_IB, color=kBlue, linewidth=2, markerstyle=21 )
SetTH1FStyle( h_MI, color=kRed,  linewidth=2, markerstyle=22 )

c = TCanvas( "corrections", "Corrections", 800, 800 )
gPad.SetRightMargin(0.05)

g_IB = TH1F2TGraph( h_IB )
g_MI = TH1F2TGraph( h_MI )

SetTH1FStyle( g_IB, color=kBlue, markerstyle=20 )
SetTH1FStyle( g_MI, color=kRed,  markerstyle=24 )
#SetTH1FStyle( g_IB, color=kBlue, fillcolor=kAzure-4, fillstyle=1001, linewidth=0, markerstyle=20, fill_alpha=0.4 )
#SetTH1FStyle( g_MI, color=kRed, fillcolor=kRed-10, fillstyle=1001, linewidth=0, markerstyle=20, fill_alpha=0.4 )

h_IB.SetMaximum( 1.5 )
h_IB.SetMinimum( 0.5 )

h_IB.GetXaxis().SetTitle( xtitle[obs] )
h_IB.GetYaxis().SetTitle( "Other method / Eikos" )
h_IB.GetXaxis().SetLabelOffset( 0.02 )

h_IB.Draw()
g_IB.Draw( "p e same")
g_MI.Draw( "p e same")

lparams = {
        'xoffset' : 0.15,
        'yoffset' : 0.90,
        'width'   : 0.70,
        'height'  : 0.04,
        }

leg = MakeLegend( lparams )
leg.SetTextFont( 42 )
leg.SetNColumns(1)
leg.AddEntry( g_IB, "D'Agostini Unfolding (N_{itr}=4)", "lep" )
leg.AddEntry( g_MI, "Simple Matrix Inversion", "lep" )
leg.Draw()
leg.SetY1( leg.GetY1() - lparams['height'] * leg.GetNRows() )


gPad.RedrawAxis()

c.SaveAs( "output/img/comparison_IB_MI.pdf")
