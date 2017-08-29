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

void Sample::SetNominalHistogramDetector( const TH1 * h, const std::string& hname ) 
{
   m_h_detector = std::make_shared<TH1D>();
   h->Copy( *m_h_detector );
}

void Sample::SetNominalHistogramResponse( const TH1 * h, const std::string& hname ) 
{ 
   m_h_response = std::make_shared<TH2D>();
   h->Copy( *m_h_response );
}

void Sample::SetNominalHistogramTruth( const TH1 * h, const std::string& hname )   
{
   m_h_truth = std::make_shared<TH1D>();
   h->Copy( *m_h_truth );
}
