#include "Sample.h"

ClassImp( Sample )

Sample::Sample( const std::string& name ) : 
  m_h_detector(NULL), m_h_response(NULL), m_h_truth(NULL)
{
  m_name      = name;
  m_latex     = name;
  m_index     = -1;
  m_type      = SAMPLE_TYPE::kSignal;
  m_color     = -1;
  m_linestyle = -1;
  m_fillstyle = -1;
}

//~~~~~~~~~~~~~~~~~~~~~~~

Sample::~Sample()
{
}

void Sample::SetNominalHistogramDetector( TH1D * h, const std::string& hname ) 
{
   m_h_detector = (TH1D*)h->Clone( hname.c_str() ); 
}

void Sample::SetNominalHistogramResponse( TH2D * h, const std::string& hname ) 
{ 
   m_h_response = (TH2D*)h->Clone( hname.c_str() ); 
}

void Sample::SetNominalHistogramTruth( TH1D * h, const std::string& hname )   
{
   m_h_truth = (TH1D*)h->Clone( hname.c_str() );    
}
