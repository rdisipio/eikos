#!/usr/bin/env python

import sys, os

#from numpy import array
from array import array
from ROOT import *

from defs import *

gROOT.SetBatch(1)

gROOT.Macro("rootlogon.C")

def SetPalette( colset = "blue2red" ):

    if colset == "blue2redB":
        stops = array( 'd', [ 0.00, 0.35, 0.65, 1.00 ] )
        
        # 286CP / 284CP / x / 177CP / 7627CP
        red   = array( 'd', [ 0.13, 0.45, 0.96, 0.74 ] )
        green = array( 'd', [ 0.31, 0.67, 0.69, 0.29 ] )
        blue  = array( 'd', [ 0.60, 0.85, 0.72, 0.14 ] )

    if colset == "blue2red":
        stops = array( 'd', [ 0.00, 0.10, 0.50, 0.90, 1.00 ] )
        # 286CP / 284CP / x / 177CP / 7627CP
        red   = array( 'd', [ 0.13, 0.45, 1.00, 0.96, 0.74 ] )
        green = array( 'd', [ 0.31, 0.67, 1.00, 0.69, 0.29 ] )
        blue  = array( 'd', [ 0.60, 0.85, 1.00, 0.72, 0.14 ] )

    TColor.CreateGradientColorTable( len(stops), stops, red, green, blue, 100 )


########################################################################

def DrawGrid( h ):
    line = TLine()
    line.SetLineWidth( 1 )
    line.SetLineColor( kWhite )
    
    xaxis = h.GetXaxis()
    yaxis = h.GetYaxis()
    
    #xaxis.SetMoreLogLabels()
    #yaxis.SetMoreLogLabels()
    
    for binx in range( 0, h.GetNbinsX() ):
        xmin = xaxis.GetBinLowEdge( binx + 1 )
        
        if not xmin == xaxis.GetXmin():
            line.DrawLine( xmin, yaxis.GetXmin(), xmin, yaxis.GetXmax() )
    
    for biny in range( 0, h.GetNbinsY() ):
        ymin = yaxis.GetBinLowEdge( biny + 1 )
        
        if not ymin == yaxis.GetXmin():
            line.DrawLine( xaxis.GetXmin(), ymin, xaxis.GetXmax(), ymin )


########################################################################


def MakeCanvas():
    c = TCanvas( "Correlation Matrix", "Correlation Matrix", 800, 800 )
    
    gPad.SetLeftMargin( 0.10 )
    gPad.SetRightMargin( 0.20 )
    gPad.SetBottomMargin( 0.15 )
    gPad.SetTopMargin( 0.05 )
    
    #c.SetLogy()
    #c.SetLogx()
    #c.SetLogz()
    
    return c


########################################################################

gStyle.SetPaintTextFormat( ".2f%" )

infilename = sys.argv[1]
infile = TFile.Open( infilename )

c = MakeCanvas()
SetPalette()
#gStyle.SetHistMinimumZero()

for hname in [ "corr_abs", "corr_rel" ]:

   h = infile.Get( hname )

   h.Draw("colz text")
   DrawGrid( h )
  
   h.GetZaxis().SetRangeUser( -1., 1. )

   h.GetZaxis().SetTitle( "Correlation" )

   h.GetZaxis().SetTitleSize( 0.05 )
   h.GetZaxis().SetTitleOffset( 1.3 )

   h.GetXaxis().SetLabelSize( 0.05 )
   h.GetYaxis().SetLabelSize( 0.05 )
   h.GetXaxis().SetTitleSize( 0.04 )
   h.GetYaxis().SetTitleSize( 0.04 )
   #h.GetXaxis().SetLabelOffset(0.01)
   h.GetXaxis().SetTitleOffset(1.3)
   h.GetYaxis().SetTitleOffset(1.3)
   h.GetXaxis().SetTickLength(0)
   h.GetYaxis().SetTickLength(0)

   lbl = "Absolute" if hname == "corr_abs" else "Normalized"

   h.GetXaxis().SetTitle( "%s differential cross-section bin" % lbl )
   h.GetYaxis().SetTitle( "%s differential cross-section bin" % lbl )

   h.SetMarkerSize(1.5)
 
   gPad.RedrawAxis()

   c.SaveAs( "output/img/%s.pdf" % ( hname ) )

