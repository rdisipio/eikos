// Header files passed as explicit arguments
#include "include/EikosUnfolder.h"

ClassImp( EikosUnfolder )

EikosUnfolder::EikosUnfolder() : 
  m_nbins(-1)
{
}

EikosUnfolder::~EikosUnfolder()
{
}

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

int EikosUnfolder::AddSample( const std::string& sample_name, double x_min, double x_max, int color, int fillstyle, int linestyle )
{
  int index = -1;

  return index;
}

int EikosUnfolder::AddSystematic( const std::string& sname, double min, double max, const std::string & latexname, const std::string & unitstring )
{
  int index = -1;

  m_systematics.push_back( new BCMTFSystematic( sname ) );
  BCMTFSystematic * p_syst = (*m_systematics.end());

  AddParameter( sname, min, max, latexname, unitstring );

  return index;
}

int EikosUnfolder::AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, const TH1D * h_u, const TH1D * h_d, const TH1D * h_n )
{
  int index = -1;

  return index;
}

int EikosUnfolder::AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, double k_u, double k_d, const TH1D * h_n )
{
   int index = -1;

   return index;
}


void EikosUnfolder::SetDiffXsTemplate( const TH1 * h )
{
  m_nbins = h->GetNbinsX();
  
  m_xedges.clear();
  for( int i = 0 ; i <= m_nbins ; i++ ) { 
     m_xedges.push_back( h->GetBinLowEdge(i+1) );
  }

  m_bw.clear();
  for( int i = 0 ; i < m_nbins ; i++ ) {
     m_bw.push_back( h->GetBinWidth(i+1) );
  }

  // set params
  char b_name[32];
  char b_latex[32];
  for( int i = 0 ; i < m_nbins ; i++ ) {
      double y = h->GetBinContent( i+1 );
      double y_min = 0.2 * y;
      double y_max = 2.0 * y;

      sprintf( b_name, "bin_%i", i+1 );
      sprintf( b_latex, "Bin %i", i+1 );
      AddParameter( b_name, 0., y_max, b_latex );
  }
}


void EikosUnfolder::SetData( const TH1D * data )
{
}


double EikosUnfolder::LogLikelihood( const std::vector<double>& parameters )
{
  double logL = 0.;

  return logL;
}


