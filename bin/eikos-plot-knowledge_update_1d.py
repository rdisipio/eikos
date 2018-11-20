#!/usr/bin/env python

import os, sys
import argparse 

from PlottingToolkit import *

from ROOT import *

gROOT.Macro( "rootlogon.C" ) 
gROOT.LoadMacro( "AtlasUtils.C" ) 
gROOT.SetBatch(1)

#gStyle.SetErrorX(0)

xtitle = {  
   "x"         : "X",
   "inclusive" : "Inclusive cross-section [pb]",
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

def Normalize( h, sf=1.0 ):
  area = h.Integral()
  h.Scale( sf / area )
  return h

#########################################################


infilename = sys.argv[1]
infile = TFile.Open( infilename )

c = TCanvas("c", "C", 1200, 800 )
gPad.SetLeftMargin( 0.17 )
gPad.SetTopMargin( 0.05 )
gPad.SetBottomMargin( 0.15 )

priors = []
posteriors = []
param = 0
while True:
  param += 1

  priors     += [ infile.Get( "prior_%i" % param ) ]
  posteriors += [ infile.Get( "posterior_%i" % param ) ]

  h_prior     = priors[-1]
  h_posterior = posteriors[-1]

  if h_prior == None: 
     exit(0)
  if h_posterior == None:     
     exit(0)


  SetTH1FStyle( h_prior,     fillstyle=1001, fillcolor=kGray+1, linewidth=0, markersize=0 )
  SetTH1FStyle( h_posterior, color=kBlack, linewidth=3, markersize=0, markerstyle=0 )

  Normalize( h_prior )
  Normalize( h_posterior )
  
  hmax = 1.3 * max( [ h_prior.GetMaximum(), h_posterior.GetMaximum() ] )
  h_prior.SetMaximum( hmax )
  h_posterior.SetMaximum( hmax )

  h_prior.Draw("h")
  h_posterior.Draw("h same")

  h_prior.GetYaxis().SetTitleOffset(1.3)
  h_prior.GetYaxis().SetLabelSize(0.06)
  h_prior.GetXaxis().SetTitleSize(0.06)
  h_prior.GetYaxis().SetTitleSize(0.06)

  lparams = {
        'xoffset' : 0.65,
        'yoffset' : 0.90,
        'width'   : 0.40,
        'height'  : 0.08,
        }

  leg = MakeLegend( lparams )
  leg.SetTextFont( 42 )
  leg.SetTextSize(0.06)
  leg.SetNColumns(1)
  leg.AddEntry( h_prior,     "Prior", "f" )
  leg.AddEntry( h_posterior, "Posterior", "f" )
  leg.Draw()
  leg.SetY1( leg.GetY1() - lparams['height'] * leg.GetNRows() )

  gPad.RedrawAxis()

  outdir = infilename.split("/")[1]
  try:
     os.mkdir( "output/%s/posteriors" % outdir )
  except:
     pass

  c.SaveAs( "output/%s/posteriors/posterior_%i.pdf" % (outdir,param) )
