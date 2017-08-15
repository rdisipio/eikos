// Header files passed as explicit arguments
#include "include/EikosUnfolder.h"

ClassImp( EikosUnfolder )

EikosUnfolder::EikosUnfolder()
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

int EikosUnfolder::AddSystematic( const std::string& sample_name, const std::string& systematic_name, const TH1D * h_u, const TH1D * h_d, const TH1D * h_n )
{
  int index = -1;

  return index;
}

void EikosUnfolder::SetData( const TH1D * data )
{
}


double EikosUnfolder::LogLikelihood( const std::vector<double>& parameters )
{
  double logL = 0.;

  return logL;
}


