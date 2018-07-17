#!/usr/bin/env python

import os, sys
from ROOT import *
from array import array

rng = TRandom3()

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


outpath = "data/toymc/"

syst = "nominal"
Nevents = 100000

known_systematics = [
  Systematic( name="syst1_u", type=SystType.multiplicative, effect=5.00,  twosided=True ),
  Systematic( name="syst1_d", type=SystType.multiplicative, effect=-5.00, twosided=True ),
  Systematic( name="syst2_u", type=SystType.multiplicative, effect=-2.00, twosided=True ),
  Systematic( name="syst2_d", type=SystType.multiplicative, effect=3.00,  twosided=True ),
  Systematic( name="syst3_u", type=SystType.additive,       effect=5.00,   twosided=True ),
  Systematic( name="syst3_d", type=SystType.additive,       effect=-5.00,  twosided=True ),
]

ofilename = "toymc.root"
ofile = TFile.Open( outpath + ofilename, "RECREATE" )
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

f_gamma_nominal = TF1("gamma_nominal", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 );
f_gamma_nominal.SetParameters( kappa_nominal, mu_nominal, theta_nominal )

f_gamma_alt1 = TF1("gamma_alt1", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 );
f_gamma_alt1.SetParameters( kappa_modelling_1, mu_modelling_1, theta_modelling_1 )

f_gamma_alt2 = TF1("gamma_alt2", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 );
f_gamma_alt2.SetParameters( kappa_modelling_2, mu_modelling_2, theta_modelling_2 )

# Efficiency and acceptance corrections
eff_nominal = 0.30
acc_nominal = 0.80
eff_modelling_1 = 0.25
acc_modelling_1 = 0.80
eff_modelling_2 = 0.35
acc_modelling_2 = 0.80

for ievent in range(Nevents):

  x_truth = f_gamma_nominal.GetRandom()
  _h['truth_nominal'].Fill(x_truth)

  # Efficiency filter
  if rng.Uniform() > eff_nominal: continue

  x_reco  = ApplyMigrations( x_truth )
  _h['response_nominal'].Fill( x_reco, x_truth )

  # Acceptance filter
  if rng.Uniform() > acc_nominal: continue

  _h['reco_nominal'].Fill( x_reco )

  for syst in known_systematics:
    y_reco = syst.Apply(x_reco)
    _h["reco_"+syst.name].Fill( y_reco )

# Do modelling systematics

for ievent in range(Nevents):
  x_truth = f_gamma_alt1.GetRandom()

  _h['truth_modelling_1'].Fill( x_truth )

  # Efficiency filter
  if rng.Uniform() > eff_modelling_1: continue

  x_reco  = ApplyMigrations( x_truth )
  _h['response_modelling_1'].Fill( x_reco, x_truth )

  # Acceptance filter
  if rng.Uniform() > acc_modelling_1: continue

  _h['reco_modelling_1'].Fill( x_reco )


for ievent in range(Nevents):
  x_truth = f_gamma_alt2.GetRandom()

  _h['truth_modelling_2'].Fill( x_truth )

  # Efficiency filter
  if rng.Uniform() > eff_modelling_2: continue

  x_reco  = ApplyMigrations( x_truth )
  _h['response_modelling_2'].Fill( x_reco, x_truth )

  # Acceptance filter
  if rng.Uniform() > acc_modelling_2: continue

  _h['reco_modelling_2'].Fill( x_reco )

ofile.Write()
ofile.Close()
