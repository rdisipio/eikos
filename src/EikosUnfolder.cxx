// Header files passed as explicit arguments
#include "include/EikosUnfolder.h"

ClassImp( EikosUnfolder )

EikosUnfolder::EikosUnfolder() : 
  m_nbins(-1), m_h_data(NULL)
{
}

EikosUnfolder::~EikosUnfolder()
{
  m_samples.clear();

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


int EikosUnfolder::AddSample( const std::string& name, SAMPLE_TYPE type, const std::string& latex, int color, int fillstyle, int linestyle )
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

  return index;
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

/////////////////////////////////


void EikosUnfolder::PrepareForRun()
{
  // Print out summary of samples  
  std::cout << "List of defined samples:" << std::endl;
  for( SampleCollection_itr_t itr = m_samples.begin() ; itr != m_samples.end() ; ++itr ) {
     const std::string& sname = itr->first;
     pSample_t p_sample = itr->second; 

     std::cout << "Sample " << p_sample->GetName() << " :: type=" << p_sample->GetType() << std::endl;
  }

  // 1) adjust posterior min/max
  pSample_t nominal = GetSignalSample();
  if( nominal == NULL ) {
     std::cout << "ERROR: invalid signal sample" << std::endl;
     return;
  }

  pTH1D_t h = nominal->GetNominalHistogramTruth();
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
       
       const double D   = m_h_data->GetBinContent( r+1 ); 
       
       const float mu   = ExpectationValue( r );
       
       logL += BCMath::LogPoisson( D, mu ); // faster!
       
       //m_posteriors_tmp[r] = mu;
  }

  return logL;
}


double EikosUnfolder::ExpectationValue( int r )
{
  double mu = 0.;

  return mu;
}
