#!/usr/bin/env python

import os, sys
from ROOT import *
from array import array

rng = TRandom3()

#############################

def Normalize( h, sf=1.0 ):
  area = h.Integral("width")
  h.Scale( sf/area )

#############################

class SystType:
   additive       = 0
   multiplicative = 1
   modelling      = 2

#~~~~~~~

class Systematic(object):

  def __init__( self, name="syst", type=SystType.multiplicative, effect=10., twosided=True ):
    self.name     = name
    self.type     = type
    self.effect   = effect
    self.twosided = twosided

  #~~~~~~~

  def Apply(self, x):
    y = 0.

    if self.type == SystType.additive:
      y = x + self.effect
    elif self.type == SystType.multiplicative:
      y = x * ( 1 + self.effect/100.)
    else:
      print "ERROR: unknown systematic type", self.type

    return y

#~~~~~~~

def ApplyMigrations(x):
   s  = 0.1 + x / 100.
   dx = rng.Gaus( 0., s )
   y  = x + dx
   return y

#############################

xs    = 250.
iLumi = 1000.
Nevents = 1000000
w = xs * iLumi / float(Nevents)

syst = "nominal"

known_systematics = [
  Systematic( name="syst1_u", type=SystType.multiplicative, effect=5.00,  twosided=True ),
  Systematic( name="syst1_d", type=SystType.multiplicative, effect=-5.00, twosided=True ),
  Systematic( name="syst2_u", type=SystType.multiplicative, effect=-2.00, twosided=True ),
  Systematic( name="syst2_d", type=SystType.multiplicative, effect=3.00,  twosided=True ),
  Systematic( name="syst3_u", type=SystType.additive,       effect=2.00,   twosided=True ),
  Systematic( name="syst3_d", type=SystType.additive,       effect=-2.00,  twosided=True ),
]

ofilename = "toymc.root"
ofile = TFile.Open( ofilename, "RECREATE" )
ofile.cd()


# Truth and reco bins do not have to be the same
xedges_truth = array( 'd', [ 0., 10., 15., 20., 25., 30., 40., 50., 70.,  100. ] )
Nbins_truth  = len(xedges_truth)-1
xedges_reco  = array( 'd', [ 0., 10., 15., 20., 25., 30., 40., 50., 70.,  100. ] )
Nbins_reco   = len(xedges_reco)-1

_h = {}

_h['truth_nominal']          = TH1F( "truth_nominal", "Observable X", Nbins_truth, xedges_truth )
_h['reco_nominal']           = TH1F( "reco_nominal",  "Observable X", Nbins_truth, xedges_truth )
_h['response_nominal']       = TH2F( "response_nominal", "Response matrix", Nbins_truth, xedges_truth, Nbins_reco, xedges_reco )

_h['truth_modelling_1']      = _h['truth_nominal'].Clone("truth_modelling_1")
_h['reco_modelling_1']       = _h['reco_nominal'].Clone("reco_modelling_1")
_h['response_modelling_1']   = _h['response_nominal'].Clone("response_modelling_1")

_h['truth_modelling_2']      = _h['truth_nominal'].Clone("truth_modelling_2")
_h['reco_modelling_2']       = _h['reco_nominal'].Clone("reco_modelling_2")
_h['response_modelling_2']   = _h['response_nominal'].Clone("response_modelling_2")

_h['data'] = _h['reco_nominal'].Clone("data")
_h['bkg']  = _h['reco_nominal'].Clone("bkg")

for syst in known_systematics:
  _h["reco_"+syst.name] = _h['reco_nominal'].Clone( "reco_%s"%syst.name )
  print "INFO: systematic %-10s: %.2f %i" % ( syst.name, syst.effect, syst.type )

# switch on event weights
for h in _h.values(): h.Sumw2()

# Observable (think of pT) is drawn from a Gamma distribution
# then smeared according to the chosen systematic
# Modelling systematics have different values of the shape and scale parameters, e.g. 4+-1 and 10+-1

kappa_nominal = 2.5
mu_nominal    = 0.
theta_nominal = 10.
kappa_modelling_1 = kappa_nominal - 0.25
mu_modelling_1    = mu_nominal
theta_modelling_1 = theta_nominal
kappa_modelling_2 = kappa_nominal
mu_modelling_2    = mu_nominal
theta_modelling_2 = theta_nominal + 1.0

f_gamma_nominal = TF1("gamma_nominal", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 )
f_gamma_nominal.SetParameters( kappa_nominal, mu_nominal, theta_nominal )

f_gamma_alt1 = TF1("gamma_alt1", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 )
f_gamma_alt1.SetParameters( kappa_modelling_1, mu_modelling_1, theta_modelling_1 )

f_gamma_alt2 = TF1("gamma_alt2", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 )
f_gamma_alt2.SetParameters( kappa_modelling_2, mu_modelling_2, theta_modelling_2 )

f_gamma_data = TF1("gamma_data", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 )
f_gamma_data.SetParameters( kappa_nominal+0.1, mu_nominal, theta_nominal-0.2 )

f_exp_bkg = TF1( "exp_bkg", "[0] * TMath::Exp( -x / [1] )", 0, 100 )
f_exp_bkg.SetParameters( 50., 100. )

# Efficiency and acceptance corrections
eff_nominal = 0.30
eff_modelling_1 = 0.25
eff_modelling_2 = 0.35
acc_nominal = 0.80

f_eff_nominal = TF1( "f_eff_nominal", "[0] + [1]*( 1.0 - TMath::Exp( -[2]*x ) )", 0, 100 )
f_eff_nominal.SetParameters( eff_nominal/3., 2.*eff_nominal/3., 0.05 )

f_acc_nominal = TF1( "f_acc_nominal", "[0] + [1]*( 1.0 - TMath::Exp( -[2]*x ) )", 0, 100 )
f_acc_nominal.SetParameters( acc_nominal/3., 2.*acc_nominal/3., 0.05 )

f_eff_modelling_1 = TF1( "f_eff_modelling_1", "[0] + [1]*( 1.0 - TMath::Exp( -[2]*x ) )", 0, 100 )
f_eff_modelling_1.SetParameters( eff_modelling_1/3., 2.*eff_modelling_1/3., 0.05 )

f_eff_modelling_2 = TF1( "f_eff_modelling_2", "[0] + [1]*( 1.0 - TMath::Exp( -[2]*x ) )", 0, 100 )
f_eff_modelling_2.SetParameters( eff_modelling_2/3., 2.*eff_modelling_2/3., 0.05 )

#f_eff_nominal     = TF1( "f_eff_nominal",     "[0]", 0., 100. )
#f_eff_modelling_1 = TF1( "f_eff_modelling_1", "[0]", 0., 100. )
#f_eff_modelling_2 = TF1( "f_eff_modelling_2", "[0]", 0., 100. )
#f_acc_nominal     = TF1( "f_acc_nominal",     "[0]", 0., 100. )

#f_eff_nominal.SetParameter( 0, eff_nominal )
#f_eff_modelling_1.SetParameter( 0, eff_nominal*1.1 )
#f_eff_modelling_2.SetParameter( 0, eff_nominal*0.9 )
#f_acc_nominal.SetParameter( 0, acc_nominal )

print "INFO: generating %i pseudo-signal events with weight %.2f" % ( Nevents, w )
for ievent in range(Nevents):

  x_truth = f_gamma_nominal.GetRandom()
  _h['truth_nominal'].Fill(x_truth, w)

  # Efficiency filter
  if rng.Uniform() > f_eff_nominal.Eval(x_truth): continue

  x_reco  = ApplyMigrations( x_truth )

  # Acceptance filter
  if rng.Uniform() > f_acc_nominal.Eval(x_reco): continue

  _h['reco_nominal'].Fill( x_reco, w )
  _h['response_nominal'].Fill( x_reco, x_truth, w )

  for syst in known_systematics:
    y_reco = syst.Apply(x_reco)
    _h["reco_"+syst.name].Fill( y_reco, w )

# Do modelling systematics

for ievent in range(Nevents):
  x_truth = f_gamma_alt1.GetRandom()

  _h['truth_modelling_1'].Fill( x_truth, w )

  # Efficiency filter
  if rng.Uniform() > f_eff_modelling_1.Eval(x_truth): continue

  x_reco  = ApplyMigrations( x_truth )

  # Acceptance filter
  if rng.Uniform() > f_acc_nominal.Eval(x_reco): continue

  _h['reco_modelling_1'].Fill( x_reco, w )
  _h['response_modelling_1'].Fill( x_reco, x_truth, w )


for ievent in range(Nevents):
  x_truth = f_gamma_alt2.GetRandom()

  _h['truth_modelling_2'].Fill( x_truth, w )

  # Efficiency filter
  if rng.Uniform() > f_eff_modelling_2.Eval(x_truth): continue

  x_reco  = ApplyMigrations( x_truth )

  # Acceptance filter
  if rng.Uniform() > f_acc_nominal.Eval(x_reco): continue

  _h['reco_modelling_2'].Fill( x_reco, w )
  _h['response_modelling_2'].Fill( x_reco, x_truth, w )


# Fill pseudo-data histogram (signal)
Nevents_data = int(xs * iLumi)
print "INFO: generating %i unweighted pseudo-data events" % Nevents_data
for ievent in range(Nevents_data):
  x_truth = f_gamma_data.GetRandom()
  if rng.Uniform() > f_eff_nominal.Eval(x_truth): continue
  x_reco = ApplyMigrations( x_truth )
  if rng.Uniform() > f_acc_nominal.Eval(x_reco): continue
  _h['data'].Fill( x_reco )

Nevents_data = _h['data'].Integral("width")
for hname, h in _h.iteritems():
  if hname.startswith("reco_"): Normalize(h, Nevents_data )

# now add background
# data and prediction drawn from the same distribution
# but statistically independent
Nevents_bkg = int(Nevents_data/10)
for ievent in range(Nevents_bkg):
  x_reco = f_exp_bkg.GetRandom()
  _h['data'].Fill( x_reco )

for ievent in range(Nevents_bkg):
  x_reco = f_exp_bkg.GetRandom()
  _h['bkg'].Fill( x_reco )


# create prediction histograms
_h['prediction_nominal'] = _h['reco_nominal'].Clone("prediction_nominal")
_h['prediction_nominal'].Add( _h['bkg'] )
for syst in known_systematics:
  _h['prediction_%s'%syst.name] = _h['reco_nominal'].Clone("prediction_%s"%syst.name)
  _h['prediction_%s'%syst.name].Add( _h['bkg'] )

# Write out to file
ofile.Write()
ofile.Close()
