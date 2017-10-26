#!/usr/bin/env python

import os,sys
from ROOT import *

gROOT.Macro( "rootlogon.C" )
gROOT.LoadMacro( "AtlasUtils.C" )

gROOT.SetBatch(1)

xtitle = {
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

def MakeATLASLabel( x, y, status = "Simulation Internal", phase_space = "" ):
    l = TLatex()
    l.SetTextSize(0.04); 
    l.SetNDC();
    l.SetTextColor(kBlack);

#    ATLAS_LABEL( x, y, kBlack )
    l.SetTextFont(72);
    l.DrawLatex(x,y,"ATLAS");

    l.SetTextFont(42)
    l.DrawLatex(  x+0.14, y, "%s #sqrt{s} = 13 TeV" % status )
#    myText( x+0.18, y, kBlack, "%s #sqrt{s} = 13 TeV" % status )

    l.DrawLatex( x, y-0.05, phase_space )

#    text = "#sqrt{s} = 13 TeV" #, 14.7 fb^{-1}"
#    l.DrawLatex( x, y-0.07, text);


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


def SetTH1FStyle( h, color = kBlack, linewidth = 1, linestyle=1, fillcolor = 0, fillstyle = 0, markerstyle = 21, markersize = 1.3 ):
    '''Set the style with a long list of parameters'''
    
    h.SetLineColor( color )
    h.SetLineWidth( linewidth )
    h.SetFillColor( fillcolor )
    h.SetFillStyle( fillstyle )
    h.SetLineStyle( linestyle )
    h.SetMarkerStyle( markerstyle )
    h.SetMarkerColor( h.GetLineColor() )
    h.SetMarkerSize( markersize )


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

phspace = "particle" 
obs = infilename.split('/')[-1].split('.')[0]

h_acc = infile.Get( "acceptance" )
h_eff = infile.Get( "efficiency" )

SetTH1FStyle( h_acc, color=kBlue, linewidth=2, markerstyle=21 )
SetTH1FStyle( h_eff, color=kRed,  linewidth=2, markerstyle=21 )

c = TCanvas( "corrections", "Corrections", 800, 800 )
gPad.SetRightMargin(0.05)

g_acc = TH1F2TGraph( h_acc )
SetTH1FStyle( g_acc, color=kBlue, fillcolor=kAzure-4, fillstyle=1001, linewidth=0, markerstyle=20 )

g_eff = TH1F2TGraph( h_eff )
SetTH1FStyle( g_eff, color=kRed, fillcolor=kRed-10, fillstyle=1001, linewidth=0, markerstyle=20 )

h_acc.SetMaximum( 1.1 )
h_acc.SetMinimum( 0. )
h_acc.GetXaxis().SetTitle( xtitle[obs] )
h_acc.GetYaxis().SetTitle( "Correction" )
h_acc.GetXaxis().SetLabelOffset( 0.02 )

h_acc.Draw()
g_eff.Draw( "p e2 same")
g_acc.Draw( "p e2 same")
#h_acc.Draw( "p same")
#h_eff.Draw( "p same")

#MakeATLASLabel( 0.15, 0.88, "Simulation Internal", "Fiducial phase space" )
#MakeATLASLabel( 0.15, 0.88, "Simulation Preliminary", "Fiducial phase space" )

lparams = {
        'xoffset' : 0.15,
        'yoffset' : 0.80,
        'width'   : 0.70,
        'height'  : 0.04,
        }

leg = MakeLegend( lparams )
leg.SetTextFont( 42 )
leg.SetNColumns(2)
  
leg.AddEntry( g_acc, "Acceptance", "pf" )
leg.AddEntry( g_eff, "Efficiency", "pf" )
leg.Draw()
leg.SetY1( leg.GetY1() - lparams['height'] * leg.GetNRows() )


gPad.RedrawAxis()

c.SaveAs( "output/img/corrections_%s.pdf" % ( obs ) )
