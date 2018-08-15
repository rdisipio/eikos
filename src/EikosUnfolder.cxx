// Header files passed as explicit arguments
#include "include/EikosUnfolder.h"
#include "BAT/BCMath.h"

ClassImp( EikosUnfolder )

EikosUnfolder::EikosUnfolder() : 
  m_nbins_truth(-1), m_nbins_reco(-1), m_regularization(kUnregularized), m_prior_shape(kPriorFlat), m_syst_initialized(false), m_obs_initialized(false),
  m_lumi(1.), m_h_data(NULL), m_h_truth(NULL), m_h_prior(NULL), m_stage_iteration(0), m_runStage(kStageUninitialized), m_bkg_name("background")
{
   gErrorIgnoreLevel = kSysError;
}

EikosUnfolder::~EikosUnfolder()
{
//  m_samples.clear();
}


/////////////////////////////////


int EikosUnfolder::GetSampleIndex( const std::string& name )
{
  int index = -1;

  return index;
}

int EikosUnfolder::GetSystematicIndex( const std::string& name )
{
  int index = -1;

  return index;
}


/////////////////////////////////

pSample_t EikosUnfolder::AddSample( const pSample_t sample )
{
   const std::string& name = sample->GetName();
   m_samples[name] = sample;

   if( sample->GetType() == kBackground ) { 
      m_bkg_name = sample->GetName();
      std::cout << "INFO: Background sample name set to " << m_bkg_name << std::endl;
   }

   std::cout << "DEBUG: EikosUnfolder: added new sample " << name << std::endl;
   return m_samples[name];
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pSample_t EikosUnfolder::AddSample( const std::string& name, SAMPLE_TYPE type, const std::string& latex, int color, int fillstyle, int linestyle )
{
  m_samples[name] = std::make_shared<Sample>();
  pSample_t p_sample = m_samples[name];

  p_sample->SetName( name );
  p_sample->SetType( type );
  p_sample->SetIndex( m_samples.size() - 1 );

  p_sample->SetLatex( latex );

  p_sample->SetColor( color );
  p_sample->SetFillStyle( fillstyle );
  p_sample->SetLineStyle( linestyle );

  if( type == kBackground ) {
     m_bkg_name = name;
     std::cout << "INFO: Background sample name set to " << m_bkg_name << std::endl;
  }

  std::cout << "DEBUG: EikosUnfolder: added new sample " << name << std::endl;

  return m_samples[name];
}


/////////////////////////////////////


int EikosUnfolder::AddSystematic( const std::string& sname, double min, double max, const std::string & latexname, const std::string & unitstring )
{

  AddParameter( sname, min, max, latexname, unitstring );

  m_syst_names.push_back( sname );

  int index = GetNParameters() - 1;

  m_syst_index[sname] = index;
  m_syst_pairs.push_back( SystPair_t( "none_u", "none_d" ) );
  m_syst_values.push_back( SystValues_t( 0., 0. ) );
  m_syst_types.push_back( kDetector );

  GetParameter(index).SetPrior(new BCGaussianPrior( 0., 1. ) );

  std::cout << "INFO: Added systematic " << sname << " with index " << index << std::endl;

  return index;
}


/////////////////////////////////

void EikosUnfolder::SetSystematicType( const std::string& sname, SYSTEMATIC_TYPE type )
{
  const int index = m_syst_index[sname] - m_nbins_truth;
  SetSystematicType( index, type );
}

void EikosUnfolder::SetSystematicType( int index, SYSTEMATIC_TYPE type )
{
   m_syst_types[index] = type;
   const std::string& sname = m_syst_names[index];
   std::cout << "INFO: Systematic " << sname << "(" << index << ") :: type = " << m_syst_types[index] << std::endl;
}

SYSTEMATIC_TYPE EikosUnfolder::GetSystematicType( int index ) const
{
   return m_syst_types[index];
}

SYSTEMATIC_TYPE EikosUnfolder::GetSystematicType( const std::string& sname ) const
{
   const int index = m_syst_index.at(sname) - m_nbins_truth;
   return GetSystematicType( index );
}

/////////////////////////////////

void EikosUnfolder::SetSystematicVariations( const std::string& sname, const std::string& var_u, const std::string& var_d )
{
   if( m_syst_index.find(sname) == m_syst_index.end() ) {
      std::cout << "ERROR: unknown systematic" << sname << std::endl;
      throw std::runtime_error( "unknown systematic" );
   }

   const int i = m_syst_index[sname] - m_nbins_truth; 

   m_syst_pairs[i].first  = var_u;
   m_syst_pairs[i].second = var_d;

   std::cout << "INFO: Systematic " << sname << "(" << i << ") :: up = " << m_syst_pairs[i].first << " :: down = " << m_syst_pairs[i].second << std::endl;
}


/////////////////////////////////


void EikosUnfolder::SetData( const TH1 * data )
{
  m_h_data = std::make_shared<TH1D>();
  data->Copy( *m_h_data );

  m_nbins_reco = m_h_data->GetNbinsX();

  m_xedges_reco.clear();
  for( int i = 0 ; i <= m_nbins_reco ; i++ ) {
     m_xedges_reco.push_back( m_h_data->GetBinLowEdge(i+1) );
  }

  m_bw_reco.clear();
  for( int i = 0 ; i < m_nbins_reco ; i++ ) {
     m_bw_reco.push_back( m_h_data->GetBinWidth(i+1) );
  }

}

/////////////////////////////////

void EikosUnfolder::SetTruth( const TH1 * truth )
{
  m_h_truth = std::make_shared<TH1D>();
  truth->Copy( *m_h_truth );

  m_nbins_truth = m_h_truth->GetNbinsX();

  m_xedges_truth.clear();
  for( int i = 0 ; i <= m_nbins_truth ; i++ ) {
     m_xedges_truth.push_back( m_h_truth->GetBinLowEdge(i+1) );
  }

  m_bw_truth.clear();
  for( int i = 0 ; i < m_nbins_truth ; i++ ) {
     m_bw_truth.push_back( m_h_truth->GetBinWidth(i+1) );
  }

  // set params
  char b_name[32];
  char b_latex[32];
  for( int i = 0 ; i < m_nbins_truth ; i++ ) {
      sprintf( b_name, "bin_%i", i+1 );
      sprintf( b_latex, "Bin %i", i+1 );
      AddParameter( b_name, -1., 2., b_latex );
  }
}

/////////////////////////////////

void EikosUnfolder::SetPrior( const TH1 * h )
{
   pTH1D_t p_h = std::make_shared<TH1D>();
   h->Copy( *p_h );
   p_h->SetName( "prior" );
   SetPrior( p_h );
}

void EikosUnfolder::SetPrior( pTH1D_t h	)
{
   if( m_h_prior == NULL ) {
     m_h_prior = std::make_shared<TH1D>();
   }
   h->Copy( (*m_h_prior) );
   m_h_prior->SetName( "prior" );

   std::cout << "INFO: new prior set." << std::endl;
}

/////////////////////////////////

void EikosUnfolder::SetPriorShape( PRIOR_SHAPE s )          
{
   m_prior_shape = s; 

   std::cout << "INFO: setting prior shape " << s << std::endl;

   if( GetPrior() == NULL ) return;

   for( int i = 0 ; i < m_h_prior->GetNbinsX() ; ++i ) {
      std::cout << "DEBUG: prior :: bin " << (i+1) << " y = " << m_h_prior->GetBinContent(i+1) << std::endl;

      if( m_prior_shape == kPriorFlat ) {
         GetParameter(i).SetPriorConstant();
         GetParameter(i).SetLimits( -1., 2. );
      }
      else if( m_prior_shape == kPriorGauss ) {
         GetParameter(i).SetPrior( new BCGaussianPrior( 0., 0.3 ) );
         GetParameter(i).SetLimits( -1., 2. );
      }
      else if( m_prior_shape == kPriorGamma ) {
         std::cout << "WARNING: Gamma prior not yet implemented. Using gaussian for now" << std::endl;
         GetParameter(i).SetPrior( new BCGaussianPrior( 0., 0.5 ) );
         GetParameter(i).SetLimits( -1., 2. );
      }
      else {
          std::cout << "ERROR: unknown prior shape " << m_regularization << std::endl;
          throw std::runtime_error( "unknown prior shape\n" );
      }
  }

}


/////////////////////////////////

void EikosUnfolder::SetSignalSample( const std::string& name )
{
   m_signal_sample = name; 
   std::cout << "INFO: Signal sample is " << m_signal_sample << std::endl;
}

pSample_t EikosUnfolder::GetSignalSample()
{
  return m_samples[m_signal_sample]; 
}

pSample_t EikosUnfolder::GetBackgroundSample( const std::string& name )
{
   if( name == "") {
     return m_samples[m_bkg_name];
   }
   else {
     return m_samples[name];
   }
}

/////////////////////////////////

void EikosUnfolder::PrepareSystematics()
{
  if( m_syst_initialized ) { 
     std::cout << "WARNING: systematics were initialized previously" << std::endl;
  }

  pSample_t signal = GetSignalSample();
  if( signal == NULL ) {
     std::cout << "ERROR: invalid signal sample" << std::endl;
     return;
  }

  pTH1D_t h_gen = signal->GetTruth( "nominal" );
  if( h_gen == NULL ) {
     std::cout << "ERROR: invalid signal truth histogram" << std::endl;
     return;
  }

  pTH1D_t h_truth_nominal = std::make_shared<TH1D>();
  h_gen->Copy( *h_truth_nominal );
  h_truth_nominal->Scale( 1./m_lumi );

  for( auto sname : m_syst_names ) {
 
     int index = m_syst_index[sname] - m_nbins_truth;

     SystPair_t spair = m_syst_pairs[index];
     const std::string& sname_u = spair.first;
     const std::string& sname_d = spair.second;

     if( m_syst_types[index] == kModelling ) {

        std::cout << "INFO: modelling systematic " << sname << "(" << index << ") / " << sname_u << " :: folding truth->reco" << std::endl;

        signal->CalculateAcceptance( sname_u );
        signal->CalculateEfficiency( sname_u );
        signal->CalculateMigrations( sname_u );

        std::string hname  = std::string("reco_") + sname_u;
        pTH1D_t p_folded_u = MakeFoldedHistogram( h_truth_nominal, sname_u, hname );
        GetSignalSample()->SetDetector( p_folded_u, sname_u );

        if( sname_d != "@symmetrize@" ) {
           std::cout << "INFO: modelling systematic " << sname << "(" << index << ") / " << sname_d << " :: folding truth->reco" << std::endl;
           signal->CalculateAcceptance( sname_d );
           signal->CalculateEfficiency( sname_d );
           signal->CalculateMigrations( sname_d );

           std::string hname  = std::string("reco_") + sname_d;
           pTH1D_t p_folded_d = MakeFoldedHistogram( h_truth_nominal, sname_d, hname );
           GetSignalSample()->SetDetector( p_folded_d, sname_d );
        }

     }
     else {
        std::cout << "INFO: detector systematic " << sname << "(" << index << ")" << std::endl;
     }


     // Calculate shifts at reco level
     pTH1D_t h_nominal = signal->GetDetector();
     for( int r = 0 ; r < m_nbins_reco ; ++r ) {
        double sigma_u = 0.;
        double sigma_d = 0.;

        pTH1D_t p_sig_u = GetSignalSample()->GetDetector(sname_u); 
        sigma_u = ( p_sig_u->GetBinContent(r+1) - h_nominal->GetBinContent(r+1) ) / h_nominal->GetBinContent(r+1);

        if( sname_d == "@symmetrize@" ) {
          sigma_d = -sigma_u;            
        }
        else {
          pTH1D_t p_sig_d = GetSignalSample()->GetDetector(sname_d);
          sigma_d = ( p_sig_d->GetBinContent(r+1) - h_nominal->GetBinContent(r+1) ) / h_nominal->GetBinContent(r+1);
        }

        if( (sigma_u>0.) && (sigma_d>0.) ) {
           sigma_u = std::max( sigma_u, sigma_d );
           sigma_d = -sigma_u;
        }
        if( (sigma_u<0.) && (sigma_d<0.) ) { 
           sigma_d = std::min( sigma_u, sigma_d );
           sigma_u = -sigma_d; 
        }

        m_syst_values[index].first.push_back( sigma_u );
        m_syst_values[index].second.push_back( sigma_d );
     }

  } // end loop over systematics

  m_syst_initialized = true;
}


/////////////////////////////////


void EikosUnfolder::PrepareForRun( RUN_STAGE run_stage )
{
  std::string syst_name = "nominal";

  // increment iteration number
  if( run_stage == m_runStage ) {
    // same stage, next iteration
    m_stage_iteration++;
  }
  else {
    // reset iteration
    m_stage_iteration = 0;
  }
  m_runStage = run_stage;

  std::cout << "INFO: run stage " << run_stage << " :: iteration " << (m_stage_iteration+1) <<  std::endl;

  // Print out summary of samples  
  std::cout << "INFO: List of defined samples (" << m_samples.size() << "):" << std::endl;
  for( SampleCollection_itr_t itr = m_samples.begin() ; itr != m_samples.end() ; ++itr ) {
     std::cout << "* ";
     pSample_t p_sample = itr->second; 

     if ( p_sample == NULL ) {
        std::cout << "WARNING: invalid sample " << std::endl;
        continue;
     }

     SAMPLE_TYPE type = p_sample->GetType();

     std::cout << "Sample " << p_sample->GetName() << " :: type=" << type << " index=" << p_sample->GetIndex() << std::endl;

     if( run_stage != kStageEstimatePrior ) continue;

     if( m_stage_iteration > 0 ) continue;

     if( type==SAMPLE_TYPE::kSignal ) {
        p_sample->CalculateAcceptance();
        p_sample->CalculateEfficiency();
        p_sample->CalculateMigrations();
     } 

  }
  std::cout << "-- end list of samples --" << std::endl;

  // check if a prior has been set
  if( GetPrior() == NULL ) {
     std::cout << "INFO: no prior set. Using nominal Monte Carlo truth to start with." << std::endl;

     pTH1D_t h_truth_nominal = std::make_shared<TH1D>(); 
     pTH1D_t h_gen = GetSignalSample()->GetTruth( syst_name );	
     h_gen->Copy( *h_truth_nominal ); 
     h_truth_nominal->Scale( 1./m_lumi );	

     SetPrior( h_truth_nominal );
     SetPriorShape( m_prior_shape );
  }
  else {
     std::cout << "INFO: prior already set. Nothing to be done here." << std::endl;
  }

  if( !m_syst_initialized ) {
    std::cout << "INFO: initializing systematics..." << std::endl;
    PrepareSystematics();
  }
  else {
    std::cout << "INFO: systematics already initialized. Nothing to be done here." << std::endl;
  }

  // Fix or Unfix systematics:
  // check if systematics have to be fixed to estimate prior
  if( m_syst_names.size() == 0 ) {
     std::cout << "INFO: there are no systematics defined." << std::endl;
  }

  for( auto sname : m_syst_names ) {
 
     if( run_stage == kStageEstimatePrior ) {
        std::cout << "INFO: stage:prior :: systematic " << sname << " is fixed to 0." << std::endl;
        GetParameter(m_syst_index[sname]).Fix(0.);
     }
     else if( run_stage == kStageStatSyst ) {
        std::cout << "INFO: stage:statsyst :: systematic " << sname << " unfixed." << std::endl;
        GetParameter(m_syst_index[sname]).Unfix();
     }
     else if( run_stage == kStageStatOnly ) {
        int i = m_syst_index[sname];
        double s0 = GetMarginalized(i).GetHistogram()->GetMean();
//        double s0 =  GetBestFitParameters()[i];
        GetParameter(m_syst_index[sname]).Fix(s0);
        std::cout << "INFO: stage:statonly :: systematic " << sname << " fixed to best-fit value " << s0 << std::endl;

//        std::cout << "DEBUG: Parameter " << sname << "(" << i << ") fixed to " << std::setprecision(4)  << s0 << " :: best-fit = " << GetBestFitParameters()[i] << std::endl;
     }
     else if( run_stage == kStageTableOfSyst ) {
        GetParameter(m_syst_index[sname]).Unfix();
     }
     else {
        GetParameter(m_syst_index[sname]).Unfix();
        std::cout << "WARNING: unknown run stage " << run_stage << " :: systematic " << sname << " unfixed." << std::endl;
     }

  } // end loop over systematics


  char b_name[32];
  char b_latex[32];
  double xs_incl = GetPrior()->Integral();
  std::cout << "INFO: prior integral = " << xs_incl << std::endl;

  // additional observables
  if( !m_obs_initialized ) {
      std::cout << "INFO: adding observables (xs incl, diffxs abs and rel)" << std::endl;

      AddObservable( "xs_incl", 0, 2.*xs_incl, "#sigma_{incl}" );

      // absolute diffxs
      for( int i = 0 ; i < m_nbins_truth ; i++ ) {
        sprintf( b_name, "bin_abs_%i", i+1 );
        sprintf( b_latex, "Bin %i (abs diffxs)", i+1 );
        double y_abs = GetPrior()->GetBinContent( i+1 );
        AddObservable( b_name, 0., 2.0*y_abs, b_latex );
      }

      // relative diffxs
      for( int i = 0 ; i < m_nbins_truth ; i++ ) {
        sprintf( b_name, "bin_rel_%i", i+1 );
        sprintf( b_latex, "Bin %i (rel diffxs)", i+1 );
        double y_abs = GetPrior()->GetBinContent( i+1 );
        double y_rel = y_abs / xs_incl;
        AddObservable( b_name, 0., 2.0*y_rel, b_latex );
      }

      m_obs_initialized = true;
  } // first iteration

}


/////////////////////////////////

pTH1D_t EikosUnfolder::MakeFoldedHistogram( pTH1D_t p_h_truth, const std::string& syst_name, const std::string& hname )
{
   if( p_h_truth == NULL ) throw std::runtime_error( "MakeFoldedHistogram: invalid input histogram\n" );

   pTH1D_t h_folded = std::make_shared<TH1D>();
   m_h_data->Copy( *(h_folded.get()) );
   h_folded->SetName( hname.c_str() );
   h_folded->Reset();

   pTH1D_t p_eff = GetSignalSample()->GetEfficiency( syst_name );
   pTH1D_t p_acc = GetSignalSample()->GetAcceptance( syst_name );
   pTH2D_t p_mig = GetSignalSample()->GetMigrations( syst_name );

   pTH1D_t h_tmp = std::make_shared<TH1D>();
   h_tmp->SetName( "h_tmp" );
   p_h_truth->Copy( *(h_tmp.get()) );

   h_tmp->Scale( m_lumi );
   h_tmp->Multiply( p_eff.get() );

   // migrations: assume y->truth, x->reco
   for( int i = 0 ; i < m_nbins_reco ; ++i ) {
     double s = 0;

     for( int j = 0 ; j < m_nbins_truth ; ++j ) {
        const double m = p_mig->GetBinContent( i+1, j+1 );

        s += m * h_tmp->GetBinContent(j+1);
     }
     h_folded->SetBinContent( i+1, s );
   }

   h_folded->Divide( p_acc.get() );

   return h_folded;
}

pTH1D_t EikosUnfolder::MakeFoldedHistogram( const std::vector<double>& parameters, const std::string& syst_name, const std::string& hname )
{
   pTH1D_t h_truth = MakeTruthHistogram( parameters );

   return MakeFoldedHistogram( h_truth, syst_name, hname );
}


/////////////////////////////////

/*
double EikosUnfolder::LogAPrioriProbability(const std::vector<double>& parameters )
{
   double logP = 0.;

   return logP;
}
*/

double EikosUnfolder::LogLikelihood( const std::vector<double>& parameters )
{
  double logL = 0.;
//  double alpha = 1.;
  double alpha = ( m_nbins_truth + m_syst_index.size() ) / float(m_nbins_truth);
  double beta = 1. / m_nbins_truth;

  auto p_bkg = GetBackgroundSample();
  auto p_sig = GetSignalSample();

  pTH1D_t p_bkg_n = p_bkg ? p_bkg->GetDetector() : NULL;
  pTH1D_t p_sig_n = p_sig ? p_sig->GetDetector() : NULL;

  pTH1D_t p_exp = MakeFoldedHistogram( parameters );
  
  for( int r = 0 ; r < m_nbins_reco ; ++r ) {
       
       double D = m_h_data->GetBinContent( r+1 );
       // Data stat unc: poisson smearing
//       D = m_rng.Poisson(D);

       double S = p_exp->GetBinContent( r+1 );
       double delta_S = 0.;
       for( size_t i = 0 ; i < m_syst_index.size() ; ++i ) {
//          const std::string& sname   = m_syst_names.at(i);
          SystPair_t spair           = m_syst_pairs.at(i);

          SystValues_t * syst_values = &( m_syst_values.at(i) );
          double sigma_u = syst_values->first.at(r);
          double sigma_d = syst_values->second.at(r);

          int    k      = i + m_nbins_truth;
          double lambda = parameters.at(k);
//          std::cout << "S :: r=" << r << " i=" << i << " k=" << k << " l=" << lambda << std::endl; 
         
          if( lambda > 0 ) delta_S += fabs(lambda)*sigma_u;
          else             delta_S += fabs(lambda)*sigma_d;
       }
       S = S * ( 1. + delta_S );

       // Background (if any)
       if( p_bkg_n == NULL ) std::cout << "WARNING: invalid nominal background" << std::endl;
       double B = p_bkg_n ? p_bkg_n->GetBinContent( r+1 ) : 0.;
       double delta_B = 0.;
       for( size_t i = 0 ; i < m_syst_index.size() ; ++i ) {

//          const std::string& sname   = m_syst_names.at(i);
          SystPair_t spair           = m_syst_pairs.at(i);
          const std::string& sname_u = spair.first;
          const std::string& sname_d = spair.second;

       	  double sigma_u = 0.;
       	  double sigma_d = 0.;

          if( p_bkg == NULL ) {
             std::cout << "WARNING: invalid background sample." << std::endl;
             return 0.;
          }

          pTH1D_t p_bkg_u, p_bkg_d;

          // upward variation
          try {
            p_bkg_u = GetBackgroundSample()->GetDetector(sname_u);
          }
          catch(...) {
            p_bkg_u = GetBackgroundSample()->GetDetector("nominal");
          }

          if( p_bkg_u == NULL ) { 
             std::cout << "ERROR: invalid background for upward systematic " << sname_u << std::endl;
          }
          sigma_u = ( p_bkg_u->GetBinContent(r+1) - p_bkg_n->GetBinContent(r+1) ) / p_bkg_n->GetBinContent(r+1); 
       	  
          // downward or symmetryzed variation
       	  if( sname_d == "@symmetrize@"	) {
       	     sigma_d = -sigma_u;
          }
       	  else {
             try { 
               p_bkg_d = p_bkg->GetDetector(sname_d);
             }
             catch(...) {
               p_bkg_d = GetBackgroundSample()->GetDetector("nominal");
             }

             if( p_bkg_d == NULL ) {
                std::cout << "ERROR: invalid background for downward systematic " << sname_d << std::endl;
             }
             sigma_d = ( p_bkg_d->GetBinContent(r+1) - p_bkg_n->GetBinContent(r+1) ) / p_bkg_n->GetBinContent(r+1);
       	  }

          if( (sigma_u>0.) && (sigma_d>0.) ) {
             sigma_u = std::max( sigma_u, sigma_d );
             sigma_d = -sigma_u;
          }
          if( (sigma_u<0.) && (sigma_d<0.) ) {
             sigma_d = std::min( sigma_u, sigma_d );
             sigma_u = -sigma_d;
          }

//          double A = TMath::Sqrt( 1./ TMath::PiOver2 ) / ( fabs(sigma_u) + fabs(sigma_d) );
//          double A = TMath::Sqrt( 0.7978845608 ) / ( fabs(sigma_u) + fabs(sigma_d) );
          int    k      = i + m_nbins_truth;
          double lambda = parameters.at(k);
//          std::cout << "B :: r=" << r << " i=" << i << " k=" << k << " l=" << lambda << std::endl;

          if( lambda > 0 ) delta_B += fabs(lambda)*sigma_u;
          else             delta_B += fabs(lambda)*sigma_d;

       }
       B = B * ( 1. + delta_B );

       S = ( S > 0. ) ? S : 0.;
       B = ( B > 0. ) ? B : 0.;
       const double mu = S + B;

 //      std::cout << "r=" << r << " D=" << D << " S=" << S << " B=" << B << " :: mu=" << mu << std::endl; 

       const double this_logL = BCMath::LogPoisson( D, mu );
       
       logL += alpha * this_logL;

  } // loop over bins

  // Regularizing term (if any)
  double S = 0.;
  if( m_regularization == kCurvature ) {
       for( int t = 1 ; t < (m_nbins_truth-1) ; t++ ) {

         const double wm = GetSignalSample()->GetTruth("nominal")->GetBinWidth(t-1+1);
         const double w0 = GetSignalSample()->GetTruth("nominal")->GetBinWidth(t+1);
         const double wp = GetSignalSample()->GetTruth("nominal")->GetBinWidth(t+1+1);

         const double cm  = GetSignalSample()->GetTruth("nominal")->GetBinCenter(t-1+1);
         const double c0  = GetSignalSample()->GetTruth("nominal")->GetBinCenter(t+1);
         const double cp  = GetSignalSample()->GetTruth("nominal")->GetBinCenter(t+1+1);

         // apply curvature to absolute diffxs

         const int offset = m_nbins_truth;
         double tm = parameters.at(t-1);
         double t0 = parameters.at(t);
         double tp = parameters.at(t+1);

/*
         const double t0 = GetObservable(1+t).Value();
         const double tp = GetObservable(1+t+1).Value();
         const double tm = GetObservable(1+t-1).Value();
*/

       // curvature
//       double Dp = ( tp - t0 );
//       double Dm = ( t0 - tm );
//       S += pow( Dp - Dm, 2 );

         const double Dp = ( (tp/wp) - (t0/w0) ) / ( cp - c0 );
         const double Dm = ( (t0/w0) - (tm/wm) ) / ( c0 - cm );

         const double curvature = fabs( Dp - Dm ) / fabs( Dp + Dm );
//         std::cout << "tm=" << tm << " t0=" << t0 << " tp=" << tp << " curv=" << curvature << " logL=" << logL << std::endl;

         S += curvature;
       } 
       logL -= alpha * S;
  } // Curvature
  else if( m_regularization == kMultinormal ) {
     for( int t = 0 ; t < m_nbins_truth ; ++t  ) {
//        const double x = parameters.at(m_nbins_truth+1+t);
        const double x = GetObservable(1+t).Value();
        const double u = GetPrior()->GetBinContent(t+1);
        const double s = u / alpha;
        //std::cout << " x=" << x << " u=" << u << " alpha=" << alpha << " s=" << s << std::endl;
        S += BCMath::LogGaus( x, u, s, false );
     }
     logL =+ S;
  } // Multinormal

//    std::cout << "DEBUG: logL = " << logL << " ::  S = " << (-S) << std::endl;

  return logL;
}


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

void EikosUnfolder::MCMCUserIterationInterface()
{
  return;
//   int npar = GetNParameters();

   for( size_t c = 0; c < fMCMCNChains; ++c ) {
      double logL = fMCMCLogLikelihood[c];
      double logP = fMCMCLogPrior[c];

      std::cout << "DEBUG: chain " << c << " :: logP = " << logP << " :: logL = " << logL << " :: logP+logL = " << (logP+logL) <<  std::endl;
   }

}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pTH1D_t EikosUnfolder::MakeTruthHistogram( const std::vector<double>& parameters )
{
   pTH1D_t p_unf = std::make_shared<TH1D>();
//   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   GetPrior()->Copy( *(p_unf.get()) );
   p_unf->Reset();
   for( int i = 0 ; i < m_nbins_truth ; ++i ) {
      double y0 = GetPrior()->GetBinContent(i+1);
      p_unf->SetBinContent( i+1, y0 * ( 1. + parameters.at(i) ) ); 
   }

   return p_unf;
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pTH1D_t EikosUnfolder::GetDiffxsAbs( const std::string hname )
{
   if( !m_obs_initialized ) throw std::runtime_error( "observables not initialized.\n" );

   pTH1D_t p_diffxs = std::make_shared<TH1D>();
//   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   GetPrior()->Copy( *(p_diffxs.get()) );
   p_diffxs->Reset();
   p_diffxs->SetName( hname.c_str() );

   for( int i = 0 ; i < m_nbins_truth ; i++ ) {

      int k = GetNParameters() + 1 + i;
      BCH1D h_post = GetMarginalized( k );

      double mean = h_post.GetHistogram()->GetMean();
      double rms  = h_post.GetHistogram()->GetRMS();
      p_diffxs->SetBinContent( i+1, mean );
      p_diffxs->SetBinError( i+1, rms );
   }

   return p_diffxs;
}


//////////////////////////////


pTH1D_t EikosUnfolder::GetDiffxsRel( const std::string hname )
{
   if( !m_obs_initialized ) throw std::runtime_error( "observables not initialized.\n" );

   pTH1D_t p_diffxs = std::make_shared<TH1D>();
//   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   GetPrior()->Copy( *(p_diffxs.get()) );
   p_diffxs->Reset();
   p_diffxs->SetName( hname.c_str() );

   for( int i = 0 ; i < m_nbins_truth ; i++ ) {
 
      int k = GetNParameters() + m_nbins_truth + 1 + i;
      BCH1D h_post = GetMarginalized( k	);

      double mean = h_post.GetHistogram()->GetMean();
      double rms  = h_post.GetHistogram()->GetRMS();
      p_diffxs->SetBinContent( i+1, mean );
      p_diffxs->SetBinError( i+1, rms );
   }

   return p_diffxs;
}

//////////////////////////////


void EikosUnfolder::CalculateObservables(const std::vector<double>& parameters)
{
   double xs_incl = 0.;
//   size_t n_params = parameters.size();
//   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   for( int i = 0 ; i < m_nbins_truth ; ++i ) { 
      double y0 = GetPrior()->GetBinContent(i+1); 
      double abs_xs = y0 * ( 1. + parameters.at(i) );
      xs_incl += abs_xs;
   }
   xs_incl = ( xs_incl > 0. ) ? xs_incl : 0.;
   GetObservable(0).Value( xs_incl );

   for( int i = 0 ; i < m_nbins_truth ; ++i ) {
      double y0 = GetPrior()->GetBinContent(i+1);
      double abs_xs = y0 * ( 1. + parameters.at(i) );
      double rel_xs = ( xs_incl > 0. ) ? abs_xs / xs_incl : 0.;

      GetObservable(i+1).Value( abs_xs );
      GetObservable(i+1+m_nbins_truth).Value( rel_xs );
   }
}


//////////////////////////////


pTH1D_t EikosUnfolder::GetSystematicsPullHistogram() 
{
   int n_syst = m_syst_index.size();

   pTH1D_t h_pull = std::make_shared<TH1D>( "pull", "Systematics pulls", n_syst, 0.5, n_syst+0.5 );

   h_pull->GetYaxis()->SetTitle( "( #theta_{fit} - #theta_{0} ) / #Delta#theta" );
   h_pull->SetMaximum(  5.0 );
   h_pull->SetMinimum( -5.0 );
   h_pull->GetXaxis()->LabelsOption( "v") ;

   for( int i = 0 ; i < n_syst ; ++i ) {
       const std::string& sname = m_syst_names.at(i);

       h_pull->GetXaxis()->SetBinLabel( i+1, sname.c_str() );

       BCH1D h_post = GetMarginalized(m_nbins_truth+i);
       double mean = h_post.GetHistogram()->GetMean();
       double rms  = h_post.GetHistogram()->GetRMS();

       h_pull->SetBinContent( i+1, mean );
       h_pull->SetBinError( i+1, rms );
   }

   return h_pull;
} 

