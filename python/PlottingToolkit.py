from ROOT import *
from array import array

def MakeCanvas( npads = 1, side = 800, split = 0.25, padding = 0.00 ):
    # assume that if pads=1 => square plot
    # padding used to be 0.05
    y_plot    = side * ( 1. - ( split + padding ) )
    y_ratio   = side * split
    y_padding = side * padding  

    height_tot = y_plot + npads * ( y_ratio + y_padding )
    height_tot = int(height_tot)

    c = TCanvas( "PredictionData", "Prediction/Data", side, height_tot )
 
    pad0 = TPad( "pad0","pad0",0, split+padding,1,1,0,0,0 )
    pad0.SetLeftMargin( 0.19 )
    pad0.SetRightMargin( 0.05 )
    pad0.SetBottomMargin( 0. )
    #pad0.SetTopMargin( 0.14 )
    pad0.SetTopMargin( 0.05 )
    pad0.Draw()
    
    pad1 = TPad( "pad1","pad1",0,0,1, split,0,0,0 )
    pad1.SetLeftMargin( 0.19 )
    pad1.SetRightMargin( 0.05 )
    pad1.SetTopMargin( 0. )
    pad1.SetGridy(1)
    pad1.SetTopMargin(0)
    pad1.SetBottomMargin(0.5)
    pad1.SetFillColor( 0 ) 
    pad1.SetFillStyle( 0 )
    pad1.Draw()
    
    pad0.cd()
    return c, pad0, pad1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def DivideByBinWidth( h ):
  nbins = h.GetNbinsX()
  for i in range(nbins):
    bw = h.GetBinWidth( i+1 )

    y  = h.GetBinContent( i+1 )
    dy = h.GetBinError( i+1 )

    h.SetBinContent( i+1, y/bw )
    h.SetBinError( i+1, dy/bw )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def SetTH1FStyle( h, color = kBlack, linewidth = 1, fillcolor = 0, fillstyle = 0, markerstyle = 21, markersize = 1.3, linestyle=kSolid, fill_alpha = 0 ):
    '''Set the style with a long list of parameters'''

    h.SetLineColor( color )
    h.SetLineWidth( linewidth )
    h.SetLineStyle( linestyle )
    h.SetFillColor( fillcolor )
    h.SetFillStyle( fillstyle )
    h.SetMarkerStyle( markerstyle )
    h.SetMarkerColor( h.GetLineColor() )
    h.SetMarkerSize( markersize )
    if fill_alpha > 0:
       h.SetFillColorAlpha( color, fill_alpha )


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def SetAxesStyle( hlist ):
    for h in hlist:
        h.GetYaxis().SetLabelSize( 0.05 )
        h.GetYaxis().SetTitleOffset( 1.6 )
        h.GetYaxis().SetTitleSize( 0.05 )
        
        h.GetXaxis().SetLabelSize( 0 )
        h.GetXaxis().SetTitleSize( 0 )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def DrawRatio( predictions, data_unc_tot, data_unc_stat=None, xtitle = "", yrange = [ 0.4, 1.6 ] ):

    nbins = data_unc_tot.GetNbinsX()
    xmin = data_unc_tot.GetXaxis().GetXmin()
    xmax = data_unc_tot.GetXaxis().GetXmax()

    # tt diffxs 7 TeV: [ 0.4, 1.6 ]    
    # tt diffxs 8 TeV: [ 0.7, 1.3 ]
    frame = gPad.DrawFrame( xmin, yrange[0], xmax, yrange[1] )
#    frame = gPad.DrawFrame( xmin, 0.7, xmax, 1.6 )

    frame.GetXaxis().SetNdivisions(508) 
    frame.GetYaxis().SetNdivisions(504)
    
    frame.GetXaxis().SetLabelSize( 0.14 )
    frame.GetXaxis().SetLabelOffset( 0.04 )
    frame.GetXaxis().SetTitleSize( 0.14 )
    frame.GetXaxis().SetTitleOffset( 1.3 )
    
    frame.GetYaxis().SetLabelSize( 0.14 )
    frame.GetYaxis().SetTitle( "#frac{Prediction}{data_unc_tot}" )
    frame.GetYaxis().SetTitleSize( 0.14 )
    frame.GetYaxis().SetTitleOffset( 0.5 )
    
    frame.GetXaxis().SetTitle( xtitle )

    frame.Draw()
    
    unc_tot  = MakeUncertaintyBand( data_unc_tot )
    unc_tot.Draw( "e2 same" )

    unc_stat = None
    if not data_unc_stat == None: 
       unc_stat = MakeUncertaintyBand( data_unc_stat )
       unc_stat.Draw( "e2 same" )

    l = TLine()
    l.SetLineStyle(kDotted)
    l.SetLineWidth(1)
    l.SetLineColor(kGray+3)
    l.DrawLine( frame.GetXaxis().GetXmin(), 1.0, frame.GetXaxis().GetXmax(), 1.0 )

    ratios = []
    for prediction in predictions:
        #r = MakeRatio( prediction, data_unc_tot )
        r = prediction.Clone( prediction.GetName() + "_ratio" )
        #r.Divide( data_unc_tot ) # wrong error propagation! double counting!
        r.Reset()
        for ibin in range(data_unc_tot.GetNbinsX()):
           y  = prediction.GetBinContent(ibin+1)
           dy = prediction.GetBinError(ibin+1)
           d  = data_unc_tot.GetBinContent(ibin+1)

           y  = y/d  if d > 0. else 0.
           dy = dy/d if d > 0. else 0.
           r.SetBinContent( ibin+1, y )
           r.SetBinError( ibin+1, dy )

        r.SetMaximum( frame.GetMaximum() )
        r.SetMinimum( frame.GetMinimum() )
        ratios += [ r ]
        r.Draw("hist e ][ same" )

        arr = TArrow()
        arr.SetLineWidth(2)
        for i in range(nbins):
          if r.GetBinContent(i+1) > yrange[1]: arr.DrawArrow( r.GetBinCenter(i+1), yrange[1]-0.15, r.GetBinCenter(i+1), yrange[1], 0.03, "|>" )
          if r.GetBinContent(i+1) < yrange[0]: arr.DrawArrow( r.GetBinCenter(i+1), yrange[0]+0.15, r.GetBinCenter(i+1),	yrange[0], 0.03, "|>" )

    gPad.RedrawAxis()

    return frame, unc_tot, unc_stat, ratios

#########################################################

def MakeUncertaintyBand( prediction ):
    unc = TGraphAsymmErrors()
    
    SetTH1FStyle( unc, color=prediction.GetLineColor(), fillstyle=1001, fillcolor=prediction.GetFillColor(), linewidth=0, markersize=0 )
    
    i = 0

    if prediction.Class() in [ TGraph().Class(), TGraphErrors.Class(), TGraphAsymmErrors().Class() ]:
       Npoints = prediction.GetN()
    else:
       Npoints = prediction.GetNbinsX()

    for n in range( Npoints ):
       if prediction.Class() in [ TGraph().Class(), TGraphErrors.Class(), TGraphAsymmErrors().Class() ]:
          x_mc = Double()
          y_mc = Double()
          prediction.GetPoint( n, x_mc, y_mc )
       else:
          x_mc = prediction.GetBinCenter(n+1)
          y_mc = prediction.GetBinContent(n+1)

       if y_mc == 0: continue
    
       unc.SetPoint( i, x_mc, 1.0 )
      
       if prediction.Class() in [ TGraph().Class(), TGraphErrors.Class(), TGraphAsymmErrors().Class() ]:  
          bw_l = prediction.GetErrorXlow( n )
          bw_h = prediction.GetErrorXhigh( n )
          err_y_lo = prediction.GetErrorYlow(n) / y_mc
          err_y_hi = prediction.GetErrorYhigh(n) / y_mc
       else:
          bw_l = prediction.GetBinWidth( n+1 ) / 2. 
          bw_h = prediction.GetBinWidth( n+1 ) / 2.
          err_y_lo = prediction.GetBinError( n+1 ) / y_mc
          err_y_hi = prediction.GetBinError( n+1 ) / y_mc

       unc.SetPointError( i, bw_l, bw_h, err_y_lo, err_y_hi )

       i += 1
  
    #unc.Print("all")
    return unc


def MakeRatio( data, prediction ):
    ratio = TGraphAsymmErrors()
    
    SetTH1FStyle( ratio, color=data.GetMarkerColor(), markerstyle=data.GetMarkerStyle(), linewidth=2 )
    
    if data.Class() in [ TGraph().Class(), TGraphErrors.Class(), TGraphAsymmErrors().Class() ]:
       nbins = data.GetN()
    else:
       nbins = data.GetNbinsX()

    i = 0
    for n in range( nbins ):
        x_mc = Double()
        y_mc = Double()
        x_data = Double()
        y_data = Double()

        if prediction.Class() in [ TGraph().Class(), TGraphErrors.Class(), TGraphAsymmErrors().Class() ]:
           prediction.GetPoint( n, x_mc, y_mc )
        else:
           x_mc = prediction.GetBinCenter( n+1 )
           y_mc = prediction.GetBinContent( n+1 )   
     
        if y_mc == 0.: continue

        if data.Class() in [ TGraph().Class(), TGraphErrors.Class(), TGraphAsymmErrors().Class() ]:
           data.GetPoint( n, x_data, y_data )
           bw = data.GetErrorXlow(n) + data.GetErrorXhigh(n)
           dy_u = data.GetErrorYhigh(n)
           dy_d = data.GetErrorYlow(n)
        else:    
           x_data = data.GetBinCenter( n+1 )
           y_data = data.GetBinContent( n+1 )
           bw = 0.# data.GetBinWidth( n+1 )
           dy_u = data.GetBinError( n+1 )
           dy_d = data.GetBinError( n+1 ) 
        
        #print '    setting point %i: %f' % (i,y_data/y_mc,)

        ratio.SetPoint( i, x_data, y_data/y_mc )
        
        ratio.SetPointError( i, bw/2, bw/2, dy_d/y_mc, dy_u/y_mc )
        
        i += 1
    return ratio


#########################################################

def MakeLegend( params ):
    leg = TLegend( params['xoffset'], params['yoffset'], params['xoffset'] + params['width'], params['yoffset'] )
    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)#0.05)
    return leg


#########################################################


def PrintATLASLabel( x = 0.2, y = 0.85, status="Internal", lumi = 0. ):
  l = TLatex()  #l.SetTextAlign(12); l.SetTextSize(tsize); 
  l.SetNDC()
  l.SetTextFont(72)
  l.SetTextColor(kBlack)
  l.DrawLatex(x,y,"ATLAS");
  l.SetTextFont(42);
  l.DrawLatex(x+0.13,y, status)
  #l.DrawLatex(x+0.14,y,"Preliminary")
  l.SetTextSize(0.04)
  s = "#sqrt{s} = 13 TeV, %2.1f fb^{-1}" % (lumi)
  l.DrawLatex(x, y-0.05, s )


#########################################################


def ScaleGraph( g, sf=1.0 ):
  nbins = g1.GetN()
  x = g1.GetX()
  y = g1.GetY()
  for i in range(nbins):
     g.SetPoint( i, x[i], sf*y[i] )

     dx = g.GetErrorXhigh(i)
     dy_l = sf * g.GetErrorYlow(i)
     dy_h = sf * g.GetErrorYhigh(i)
     g.SetPointError( i, dx, dx, dy_l, dy_h )

#~~~~~~~~~~~~~~~~~~

def AddGraphs( g1, g2, hname, sf1=1.0, sf2=1.0 ):
  g = TGraphAsymmErrors()
  g.SetName( hname )

  nbins = g1.GetN()

  x  = g1.GetX()
  y1 = g1.GetY()
  y2 = g2.GetY()

  for i in range(nbins):
     y = sf1*y1[i] + sf2*y2[i]
     g.SetPoint( i, x[i], y )

     dx = g1.GetErrorXhigh(i)
     bw = 2.*dx

     dy1_l = bw*sf1*g1.GetErrorYlow(i)
     dy1_h = bw*sf1*g1.GetErrorYhigh(i)
     dy2_l = bw*sf2*g2.GetErrorYlow(i)
     dy2_h = bw*sf2*g2.GetErrorYhigh(i)

     dy_l = TMath.Sqrt( dy1_l*dy1_l + dy2_l*dy2_l ) / bw
     dy_h = TMath.Sqrt( dy1_h*dy1_h + dy2_h*dy2_h ) / bw

     g.SetPointError( i, dx, dx, dy_l, dy_h )

  return g

#~~~~~~~~~~~~~~~~~~~~~~~~

def RebinGraph( g, rebin=2, div_by_bw=True ):
   Nbins = g.GetN()
   x      = g.GetX()
   y      = g.GetY()  
   dy_u   = g.GetEYhigh()
   dy_d   = g.GetEYlow()
   dx_l   = g.GetEXlow()

   xedges = array( 'd', [0.]*(Nbins+1) )
   for i in range(Nbins): xedges[i] = x[i]-dx_l[i]
   xedges[Nbins] = x[Nbins-1] + dx_l[Nbins-1]
   print xedges

   h_u = TH1D( "h_u", "HU", Nbins, xedges[0], xedges[-1] )
   h_d = TH1D( "h_d", "HD", Nbins, xedges[0], xedges[-1] )
   for i in range(Nbins):
      h_u.SetBinContent( i+1, y[i] )
      h_u.SetBinError( i+1, dy_u[i] )

      h_d.SetBinContent( i+1, y[i] )
      h_d.SetBinError( i+1, dy_d[i] )

   h_u.Rebin( rebin )
   h_d.Rebin( rebin )

#   DivideByBinWidth( h_u )
#   DivideByBinWidth( h_d )

   g_new = TGraphAsymmErrors()
   for i in range(Nbins):
      x_i  = h_u.GetBinCenter( i+1 ) 
      bw_i = h_u.GetBinWidth( i+1 ) 
      y_i  = h_u.GetBinContent( i+1 ) 

      dy_u_i = h_u.GetBinError( i+1 ) 
      dy_d_i = h_d.GetBinError(	i+1 ) 

      g_new.SetPoint( i, x_i, y_i )
      g_new.SetPointError( i, bw_i/2., bw_i/2., dy_d_i, dy_u_i )

   return g_new
