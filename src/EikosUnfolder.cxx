// Header files passed as explicit arguments
#include "include/EikosUnfolder.h"

ClassImp( EikosUnfolder )

EikosUnfolder::EikosUnfolder() : 
  m_nbins(-1), m_lumi(1.), m_h_data(NULL)
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
  int index = -1;

  m_systematics.push_back( new BCMTFSystematic( sname ) );
  BCMTFSystematic * p_syst = (*m_systematics.end());

  AddParameter( sname, min, max, latexname, unitstring );

  return index;
}


/////////////////////////////////


int EikosUnfolder::AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, const pTH1D_t h_u, const pTH1D_t h_d, const pTH1D_t h_n )
{
  int index = -1;

  return index;
}

int EikosUnfolder::AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, double k_u, double k_d, const pTH1D_t h_n )
{
   int index = -1;

   return index;
}


/////////////////////////////////


void EikosUnfolder::SetData( const TH1 * data )
{
  m_h_data = std::make_shared<TH1D>();
  data->Copy( *m_h_data );
//  m_h_data- (TH1D*)data->Clone( "data" ) );

  m_nbins = m_h_data->GetNbinsX();

  m_v_data = std::make_shared<TMatrixD>( m_nbins, 1 );
  for( int i = 0 ; i < m_nbins ; ++i ) (*m_v_data)[i][0] = data->GetBinContent(i+1);

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
//      SetPriorConstant( i );
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
  for( int i = 0 ; i < m_nbins ; i++ ) {
      double y = h->GetBinContent( i+1 ) / m_lumi;
      double y_min = 0.2 * y;
      double y_max = 2.0 * y;
      double dy    = ( y_max - y_min ) / 2.;

      sprintf( b_name, "bin_%i", i+1 );
      BCParameter * np = &GetParameter( b_name );
      np->SetLimits( y_min, y_max );

      SetPriorGauss( i, y, dy );
  }

}


/////////////////////////////////


double EikosUnfolder::LogLikelihood( const std::vector<double>& parameters )
{
  double logL = 0.;

  copy( parameters.begin(), parameters.end(), back_inserter(m_parameters) );

  pTH1D_t p_exp = MakeUnfolded();
  pTH1D_t p_eff = GetSignalSample()->GetEfficiency();
  pTH1D_t p_acc = GetSignalSample()->GetAcceptance();
  pTH1D_t p_bkg = GetBackgroundSample()->GetDetector();

  p_exp->Scale( m_lumi );
  p_exp->Multiply( p_eff.get() );
  // migrations here
  p_exp->Multiply( p_acc.get() );

  for( int r = 0 ; r < m_nbins ; ++r ) {
       
       const double D = m_h_data->GetBinContent( r+1 );
       const double S = p_exp->GetBinContent( r+1 );
       const double B = p_bkg->GetBinContent( r+1 );

       const double mu = S + B;

//       std::cout << "r =" << r << " D = " << D << " :: mu = " << mu << std::endl; 
       
       logL += BCMath::LogPoisson( D, mu );
       
       //m_posteriors_tmp[r] = mu;
  }

  return logL;
}


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pTH1D_t EikosUnfolder::MakeUnfolded()
{
   pTH1D_t p_unf = std::make_shared<TH1D>();
   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   p_gen->Copy( *(p_unf.get()) );
   p_unf->Reset();
   for( int i = 0 ; i < m_nbins ; ++i ) p_unf->SetBinContent( i+1, m_parameters.at(i) ); 

   return p_unf;
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pTH1D_t EikosUnfolder::GetDiffxsAbs()
{
   std::vector<double> bestfit = GetBestFitParameters();

   pTH1D_t p_diffxs = std::make_shared<TH1D>();
   pTH1D_t p_gen = GetSignalSample()->GetTruth();

   p_gen->Copy( *(p_diffxs.get()) );
   p_diffxs->Reset();

   for( int i = 0 ; i < m_nbins ; i++ ) {
       p_diffxs->SetBinContent( i+1, bestfit.at(i) );
   }

   return p_diffxs;
}
