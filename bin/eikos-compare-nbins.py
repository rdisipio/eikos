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
    dx = 0.
    x += offset*bw

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

infile_isoconstrained   = TFile.Open( "output/toymc_statonly_isoconstrained/x.toymc.statonly.isoconstrained.root" )
infile_underconstrained = TFile.Open( "output/toymc_statonly_underconstrained/x.toymc.statonly.underconstrained.root" )
infile_overconstrained  = TFile.Open( "output/toymc_statonly_overconstrained/x.toymc.statonly.overconstrained.root" )

hname = "diffxs_statsyst_abs"

h_isoconstrained   = infile_isoconstrained.Get( hname )
h_underconstrained = infile_underconstrained.Get( hname )   
h_overconstrained  = infile_overconstrained.Get( hname )  

h_norm = h_isoconstrained.Clone("h_norm")
DivideBy( h_isoconstrained,   h_norm )
DivideBy( h_underconstrained, h_norm )
DivideBy( h_overconstrained,  h_norm )

c = TCanvas( "c", "C", 800, 800 )
gPad.SetRightMargin(0.05)

g_isoconstrained   = TH1F2TGraph( h_isoconstrained )
g_underconstrained = TH1F2TGraph( h_underconstrained, 0.1 ) 
g_overconstrained  = TH1F2TGraph( h_overconstrained, -0.1 )

#SetTH1FStyle( h_isoconstrained,   fillstyle=1001, color=kYellow, fillcolor=kYellow )
SetTH1FStyle( h_isoconstrained,   fillstyle=1001, color=kGray+1, fillcolor=kGray+1, markersize=0, linewidth=0 )
SetTH1FStyle( g_underconstrained, color=kBlue, markerstyle=21 )
SetTH1FStyle( g_overconstrained,  color=kRed, markerstyle=24 )

h_isoconstrained.SetMaximum( 1.6 )
h_isoconstrained.SetMinimum( 0.5 )

h_isoconstrained.GetXaxis().SetTitle( "X" )
h_isoconstrained.GetYaxis().SetTitle( "Ratio to isoconstrained" )

h_isoconstrained.Draw( "e2" )
l = TLine()
l.SetLineStyle(kDashed)
l.SetLineColor(kGray+3)
l.SetLineWidth(2)
l.DrawLine( 0, 1., 100., 1. )

g_underconstrained.Draw( "p e same")
g_overconstrained.Draw( "p e same")

print "INFO: isoconstrained:"
g_isoconstrained.Print("all")
print "INFO: underconstrained:"
g_underconstrained.Print("all")
print "INFO: overconstrained:"
g_overconstrained.Print("all")

lparams = {
        'xoffset' : 0.15,
        'yoffset' : 0.90,
        'width'   : 0.35,
        'height'  : 0.04,
        }

leg = MakeLegend( lparams )
leg.SetTextFont( 42 )
leg.SetNColumns(1)
leg.AddEntry( h_isoconstrained,   "N_{reco} = N_{truth}", "fp") 
leg.AddEntry( g_underconstrained, "N_{reco} < N_{truth}", "lp")
leg.AddEntry( g_overconstrained,  "N_{reco} > N_{truth}", "lp")
leg.Draw()
leg.SetY1( leg.GetY1() - lparams['height'] * leg.GetNRows() )

gPad.RedrawAxis()

c.SaveAs( "output/img/comparison_nbins.pdf")

