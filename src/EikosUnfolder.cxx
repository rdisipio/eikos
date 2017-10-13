// Header files passed as explicit arguments
#include "include/EikosUnfolder.h"

ClassImp( EikosUnfolder )

EikosUnfolder::EikosUnfolder() : 
  m_nbins(-1), m_regularization(kMultinomial), m_lumi(1.), m_h_data(NULL)
{
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
   return m_samples[name];
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pSample_t EikosUnfolder::AddSample( const std::string& name, SAMPLE_TYPE type, const std::string& latex, int color, int fillstyle, int linestyle )
{
  int index = -1;

  m_samples[name] = std::make_shared<Sample>();
  pSample_t p_sample = m_samples[name];

  p_sample->SetName( name );
  p_sample->SetType( type );
  p_sample->SetIndex( m_samples.size() - 1 );

  p_sample->SetLatex( latex );

  p_sample->SetColor( color );
  p_sample->SetFillStyle( fillstyle );
  p_sample->SetLineStyle( linestyle );

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

  GetParameter(index).SetPrior(new BCGaussianPrior( 0., 1. ) );

  std::cout << "Added systematic " << sname << " with index " << index << std::endl;

  return index;
}


/////////////////////////////////

void EikosUnfolder::SetSystematicVariations( const std::string& sname, const std::string& var_u, const std::string& var_d )
{
   if( m_syst_index.find(sname) == m_syst_index.end() ) {
      std::cout << "ERROR: unknown systematic" << sname << std::endl;
      throw std::runtime_error( "unknown systematic" );
   }

   const int i = m_syst_index[sname] - m_nbins; 

   m_syst_pairs[i].first  = var_u;
   m_syst_pairs[i].second = var_d;

   std::cout << "Systematic " << sname << "(" << i << ") :: up = " << m_syst_pairs[i].first << " :: down = " << m_syst_pairs[i].second << std::endl;
}


/////////////////////////////////


void EikosUnfolder::SetData( const TH1 * data )
{
  m_h_data = std::make_shared<TH1D>();
  data->Copy( *m_h_data );
//  m_h_data- (TH1D*)data->Clone( "data" ) );

  m_nbins = m_h_data->GetNbinsX();

//  m_v_data = std::make_shared<TMatrixD>( m_nbins, 1 );
//  for( int i = 0 ; i < m_nbins ; ++i ) (*m_v_data)[i][0] = data->GetBinContent(i+1);

  m_xedges.clear();
  for( int i = 0 ; i <= m_nbins ; i++ ) {
     m_xedges.push_back( m_h_data->GetBinLowEdge(i+1) );
  }

  m_bw.clear();
  for( int i = 0 ; i < m_nbins ; i++ ) {
     m_bw.push_back( m_h_data->GetBinWidth(i+1) );
  }

  // set params
  char b_name[32];
  char b_latex[32];
  for( int i = 0 ; i < m_nbins ; i++ ) {
      sprintf( b_name, "bin_%i", i+1 );
      sprintf( b_latex, "Bin %i", i+1 );
      AddParameter( b_name, 0., 1., b_latex );
  }
}


/////////////////////////////////

void EikosUnfolder::SetSignalSample( const std::string& name )
{
   m_signal_sample = name; 
   std::cout << "Signal sample is " << m_signal_sample << std::endl;
}

pSample_t EikosUnfolder::GetSignalSample()
{
  return m_samples[m_signal_sample]; 
}

pSample_t EikosUnfolder::GetBackgroundSample( const std::string& name )
{
  return m_samples[name];
}

/////////////////////////////////


void EikosUnfolder::PrepareForRun()
{
/*
  // Create background sample
  pSample_t background = std::make_shared<Sample>( "background", SAMPLE_TYPE::kBackground, "Total background" );    
  pTH1D_t h_bkg = std::make_shared<TH1D>();
  m_h_data->Copy(*h_bkg);
  h_bkg->Reset();
  h_bkg->SetName( "background" );
*/

  std::string syst_name = "nominal";

  // Print out summary of samples  
  std::cout << "List of defined samples:" << std::endl;
  for( SampleCollection_itr_t itr = m_samples.begin() ; itr != m_samples.end() ; ++itr ) {
//     const std::string& sname = itr->first;
     pSample_t p_sample = itr->second; 
     SAMPLE_TYPE type = p_sample->GetType();

     std::cout << "Sample " << p_sample->GetName() << " :: type=" << type << std::endl;

     if( type==SAMPLE_TYPE::kSignal ) {
        p_sample->CalculateAcceptance();
        p_sample->CalculateEfficiency();
        p_sample->CalculateMigrations();
     } 

/*
     if( (type==SAMPLE_TYPE::kBackground) || (type==SAMPLE_TYPE::kDataDriven) ) {
        pTH1D_t h_sample;
        p_sample->GetDetector( h_sample, syst_name );

        if( h_sample == NULL ) std::cout << "ERROR: invalid histogram for sample " << p_sample->GetName() << std::endl;
        h_bkg->Add( h_sample.get() );
     }
*/
  }

//  background->SetDetector( h_bkg, syst_name );
//  AddSample( background );
  
  // 1) adjust posterior min/max
  pSample_t nominal = GetSignalSample();
  if( nominal == NULL ) {
     std::cout << "ERROR: invalid signal sample" << std::endl;
     return;
  }

  pTH1D_t h = nominal->GetTruth( syst_name );
  if( h == NULL ) {
     std::cout << "ERROR: invalid signal truth histogram" << std::endl;
     return;
  }

  char b_name[32];
  double xs_incl = 0.;
  for( int i = 0 ; i < m_nbins ; i++ ) {
      double y = h->GetBinContent( i+1 ) / m_lumi;
      double y_min = 0. * y;
      double y_max = 2.0 * y;
      double dy    = 0.2*( y_max - y_min );
//      double dy = h->GetBinError( i+1 ) / m_lumi;
      xs_incl += y;

      sprintf( b_name, "bin_%i", i+1 );
      BCParameter * np = &GetParameter( b_name );
      np->SetLimits( 0., y_max );

      if( m_regularization == kUnregularized ) {
         GetParameter(i).SetPriorConstant();
      }
      else if( m_regularization == kMultinomial ) { 
          GetParameter(i).SetPrior(new BCPositiveDefinitePrior(new BCGaussianPrior( y, dy ) ) );
      }
      else {
          std::cout << "ERROR: unknown regularization method " << m_regularization << std::endl;
          throw std::runtime_error( "unknown regularization method" );
      }
  }

  // additional observables
  AddObservable( "xs_incl", 0.5*xs_incl, 1.5*xs_incl, "#sigma_{incl}" );

}


/////////////////////////////////

pTH1D_t EikosUnfolder::MakeFoldedHistogram( const std::vector<double>& parameters )
{
   pTH1D_t h_folded = MakeTruthHistogram( parameters );

   pTH1D_t p_eff = GetSignalSample()->GetEfficiency();
   pTH1D_t p_acc = GetSignalSample()->GetAcceptance();
   pTH2D_t p_mig = GetSignalSample()->GetMigrations();

   h_folded->Scale( m_lumi );

   h_folded->Multiply( p_eff.get() );

   // migrations
   TH1D * h_tmp = (TH1D*)h_folded->Clone( "h_tmp" );

   for( int i = 0 ; i < p_mig->GetNbinsX() ; ++i ) {
     double x = 0;

     for( int j = 0 ; j < p_mig->GetNbinsY() ; ++j ) {
        double m = p_mig->GetBinContent( i+1, j+1 );

        x += h_folded->GetBinContent(j+1) * m;
     }
     h_tmp->SetBinContent( i+1, x );
   }
   for( int i = 0 ; i < m_nbins ; ++i ) {
      h_folded->SetBinContent( i+1, h_tmp->GetBinContent(i+1) );
   }
   delete h_tmp;

   h_folded->Divide( p_acc.get() );

   return h_folded;
}


/////////////////////////////////


double EikosUnfolder::LogLikelihood( const std::vector<double>& parameters )
{
  double logL = 0.;

//  std::cout << "p1=" << parameters.at(0) << " p2=" << parameters.at(1) << " p3=" << parameters.at(2) << std::endl;
//  copy( parameters.begin(), parameters.end(), back_inserter(m_parameters) );

  pTH1D_t p_bkg = GetBackgroundSample() ? GetBackgroundSample()->GetDetector() : NULL;
  pTH1D_t p_nominal = GetSignalSample()->GetDetector();

  pTH1D_t p_exp = MakeFoldedHistogram( parameters );
  
  for( int r = 0 ; r < m_nbins ; ++r ) {
       
       double D = m_h_data->GetBinContent( r+1 );
       // Data stat unc: poisson smearing
//       D = m_rng.Poisson(D);

       double S = p_exp->GetBinContent( r+1 );
       for( int i = 0 ; i < m_syst_index.size() ; ++i ) {
          const std::string& sname   = m_syst_names.at(i);
          SystPair_t spair           = m_syst_pairs.at(i); 
          const std::string& sname_u = spair.first;
          const	std::string& sname_d = spair.second;

          double sigma_u = 0.;
          double sigma_d = 0.;

          pTH1D_t p_sig_u = GetSignalSample()->GetDetector(sname_u);
          sigma_u = p_sig_u->GetBinContent(r+1) - p_nominal->GetBinContent(r+1);

          if( sname_d == "@symmetrize@" ) {
             sigma_d = -sigma_u;            
          }
          else {
             pTH1D_t p_sig_d = GetSignalSample()->GetDetector(sname_d);
             sigma_d = p_sig_d->GetBinContent(r+1) - p_nominal->GetBinContent(r+1);
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

          int    k      = i + m_nbins;
          double lambda = parameters.at(k);
//          std::cout << "S :: r=" << r << " i=" << i << " k=" << k << " l=" << lambda << std::endl; 
         
          if( lambda > 0 ) S += fabs(lambda)*sigma_u;
          else             S += fabs(lambda)*sigma_d;

       }

       double B = p_bkg ? p_bkg->GetBinContent( r+1 ) : 0.;
       for( int i = 0 ; i < m_syst_index.size() ; ++i ) {

          const std::string& sname   = m_syst_names.at(i);
          SystPair_t spair           = m_syst_pairs.at(i);
          const std::string& sname_u = spair.first;
          const std::string& sname_d = spair.second;

       	  double sigma_u = 0.;
       	  double sigma_d = 0.;

          pTH1D_t p_bkg_u = GetBackgroundSample()->GetDetector(sname_u);
          sigma_u = p_bkg_u->GetBinContent(r+1) - p_bkg->GetBinContent(r+1); 
       	  
       	  if( sname_d == "@symmetrize@"	) {
       	     sigma_d = -sigma_u;
          }
       	  else {
             pTH1D_t p_bkg_d = GetBackgroundSample()->GetDetector(sname_d);
             sigma_d = p_bkg_d->GetBinContent(r+1) - p_bkg->GetBinContent(r+1);
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
          int    k      = i + m_nbins;
          double lambda = parameters.at(k);
//          std::cout << "B :: r=" << r << " i=" << i << " k=" << k << " l=" << lambda << std::endl;

          if( lambda > 0 ) B += fabs(lambda)*sigma_u;
          else             B += fabs(lambda)*sigma_d;

       }

       S = ( S > 0. ) ? S : 0.;
       B = ( B > 0. ) ? B : 0.;
       const double mu = S + B;

 //      std::cout << "r=" << r << " D=" << D << " S=" << S << " B=" << B << " :: mu=" << mu << std::endl; 
       
       logL += BCMath::LogPoisson( D, mu );
  }
//  std::cout << "logL = " << logL << std::endl;

  return logL;
}


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pTH1D_t EikosUnfolder::MakeTruthHistogram( const std::vector<double>& parameters )
{
   pTH1D_t p_unf = std::make_shared<TH1D>();
   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   p_gen->Copy( *(p_unf.get()) );
   p_unf->Reset();
   for( int i = 0 ; i < m_nbins ; ++i ) p_unf->SetBinContent( i+1, parameters.at(i) ); 

   return p_unf;
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pTH1D_t EikosUnfolder::GetDiffxsAbs()
{
//   std::vector<double> bestfit = GetBestFitParameters();

   pTH1D_t p_diffxs = std::make_shared<TH1D>();
   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   p_gen->Copy( *(p_diffxs.get()) );
   p_diffxs->Reset();
 
   for( int i = 0 ; i < m_nbins ; i++ ) {
      BCH1D h_post = GetMarginalized(i);
      double mean = h_post.GetHistogram()->GetMean();
      double rms  = h_post.GetHistogram()->GetRMS();
      p_diffxs->SetBinContent( i+1, mean );
      p_diffxs->SetBinError( i+1, rms );
   }

   return p_diffxs;
}


void EikosUnfolder::CalculateObservables(const std::vector<double>& parameters)
{
   double xs_incl = 0.;
   for( int i = 0 ; i < m_nbins ; ++i ) xs_incl += parameters.at(i);

   GetObservable(0).Value( xs_incl );
}
