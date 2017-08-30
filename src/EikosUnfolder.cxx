// Header files passed as explicit arguments
#include "include/EikosUnfolder.h"

ClassImp( EikosUnfolder )

EikosUnfolder::EikosUnfolder() : 
  m_nbins(-1), m_h_data(NULL)
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
  for( int i = 0 ; i < m_nbins ; ++i ) (*m_v_data)[i] = data->GetBinContent(i+1);

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
      SetPriorConstant( i );
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

pSample_t EikosUnfolder::GetBackgroundSample()
{
  return m_samples["background"];
}

/////////////////////////////////


void EikosUnfolder::PrepareForRun()
{
  // Create background sample
  pSample_t background = std::make_shared<Sample>( "background", SAMPLE_TYPE::kBackground, "Total background" );    
  pTH1D_t h_bkg = std::make_shared<TH1D>();
  m_h_data->Copy(*h_bkg);
  h_bkg->Reset();
  h_bkg->SetName( "background" );

  // Print out summary of samples  
  std::cout << "List of defined samples:" << std::endl;
  for( SampleCollection_itr_t itr = m_samples.begin() ; itr != m_samples.end() ; ++itr ) {
//     const std::string& sname = itr->first;
     pSample_t p_sample = itr->second; 
     SAMPLE_TYPE type = p_sample->GetType();

     std::cout << "Sample " << p_sample->GetName() << " :: type=" << type << std::endl;

     if( (type==SAMPLE_TYPE::kBackground) || (type==SAMPLE_TYPE::kDataDriven) ) {
        pTH1D_t h_sample = p_sample->GetNominalDetector_histogram();
        h_bkg->Add( h_sample.get() );
     }
  }
  background->SetNominalDetector(h_bkg.get());
  AddSample( background );
  
  // 1) adjust posterior min/max
  pSample_t nominal = GetSignalSample();
  if( nominal == NULL ) {
     std::cout << "ERROR: invalid signal sample" << std::endl;
     return;
  }

  pTH1D_t h = nominal->GetNominalTruth_histogram();
  if( h == NULL ) {
     std::cout << "ERROR: invalid signal truth histogram" << std::endl;
     return;
  }

  char b_name[32];
  for( int i = 0 ; i < m_nbins ; i++ ) {
      double y = h->GetBinContent( i+1 );
      double y_min = 0.2 * y;
      double y_max = 2.0 * y;

      sprintf( b_name, "bin_%i", i+1 );
      BCParameter * np = &GetParameter( b_name );
      np->SetLimits( y_min, y_max );
  }

}


/////////////////////////////////


double EikosUnfolder::LogLikelihood( const std::vector<double>& parameters )
{
  double logL = 0.;

  copy( parameters.begin(), parameters.end(), back_inserter(m_parameters) );

  for( int r = 0 ; r < m_nbins ; ++r ) {
       
       const double D  = (*m_v_data)( r, 0 );
       const double mu = ExpectationValue( r );
//       std::cout << "r =" << r << " D = " << D << " :: mu = " << mu << std::endl; 
       
       logL += BCMath::LogPoisson( D, mu );
       
       //m_posteriors_tmp[r] = mu;
  }

  return logL;
}


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


double EikosUnfolder::ExpectationValue( int r )
{
  double mu = 0.;

  float S = 0.;
  for( int t = 0 ; t < m_nbins ; ++t ) {
     const double eff = RecoProb( r, t );
     S += m_parameters.at( t ) * eff;
  }
  S = ( S >= 0. ) ? S : 0.;

  pTMatrixD_t bkg = GetBackgroundSample()->GetNominalDetector_vector();  
  double B = 0.;
  B = (*bkg)(r,0);
  B = ( B >= 0. ) ? B : 0.;

  mu = S + B;
  mu = ( mu >= 0. ) ? mu : 0.;

  return mu;
}


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


double EikosUnfolder::RecoProb( const int r, const int t )
{   
   double p = 1.;

   pSample_t nominal = GetSignalSample();
   pTMatrixD_t M = nominal->GetNominalResponse_matrix();
   
   double m = (*M)(t,r);

   double sumD = 0.;
   for(unsigned int k = 0 ; k < m_nbins ; k++ ) {
      sumD += (*M)(t,k);
   }

   p = m / sumD;

   return p;
}
