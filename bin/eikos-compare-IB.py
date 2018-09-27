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


def SetTH1FStyle( h, color = kBlack, linewidth = 2, linestyle=1, fillcolor = 0, fillstyle = 0, markerstyle = 21, markersize = 1.5, fill_alpha=0.0 ):
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

def TH1F2TGraph(h, offset=0.):
  g = TGraphErrors()
  g.SetName( "g_%s" % h.GetName() )

  Nbins = h.GetNbinsX()
  for i in range(Nbins):
    x = h.GetBinCenter( i+1 )
    y = h.GetBinContent( i+1 )
    bw = h.GetBinWidth( i+1 )
    dy = h.GetBinError( i+1 )
    x += offset*bw
#    dx = 0.
    dx = 0. if not offset==0. else bw/2

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

infilename = sys.argv[1]
infile = TFile.Open( infilename )

obs = infilename.split('/')[-1].split('.')[0]

h_eikos = infile.Get( "diffxs_statsyst_rel" )
h_IB    = infile.Get( "diffxs_IB_rel" )
h_MI    = infile.Get( "diffxs_MI_rel" )

h_unc = h_eikos.Clone("h_unc")
DivideBy( h_unc, h_eikos )
DivideBy( h_IB,  h_eikos )
DivideBy( h_MI,  h_eikos )

c = TCanvas( "corrections", "Corrections", 800, 800 )
gPad.SetRightMargin(0.05)

g_unc = TH1F2TGraph( h_unc ) 
g_IB  = TH1F2TGraph( h_IB, offset=0.1 )
g_MI  = TH1F2TGraph( h_MI, offset=-0.1 )

SetTH1FStyle( g_unc, fillcolor=kGray+1, fillstyle=1001, linewidth=0, markersize=0 )
SetTH1FStyle( g_IB, color=kBlue, markerstyle=20, markersize=1.5 )
SetTH1FStyle( g_MI, color=kRed,  markerstyle=25, markersize=1.5 )

g_unc.SetMaximum( 1.6 )
g_unc.SetMinimum( 0.5 )

g_unc.GetXaxis().SetTitle( xtitle[obs] )
g_unc.GetYaxis().SetTitle( "Other method / Eikos" )
g_unc.GetXaxis().SetLabelOffset( 0.02 )

g_unc.Draw( "a e2" )
l = TLine()
l.SetLineStyle(kDashed)
l.SetLineWidth(2)
l.SetLineColor(kGray+3)
l.DrawLine( 0, 1., 100., 1. )

g_IB.Draw( "p e same")
g_MI.Draw( "p e same")

lparams = {
        'xoffset' : 0.15,
        'yoffset' : 0.90,
        'width'   : 0.35,
        'height'  : 0.04,
        }

leg = MakeLegend( lparams )
leg.SetTextFont( 42 )
leg.SetNColumns(1)
leg.AddEntry( g_IB, "D'Agostini Unfolding (N_{itr}=4)", "lp" )
leg.AddEntry( g_MI, "Simple Matrix Inversion", "lp" )
leg.AddEntry( g_unc, "Eikos Stat. Unc.", "f" )
leg.Draw()
leg.SetY1( leg.GetY1() - lparams['height'] * leg.GetNRows() )


gPad.RedrawAxis()

c.SaveAs( "output/img/comparison_IB_MI.pdf")
