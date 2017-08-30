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

void Sample::SetNominalDetector( const TH1 * h, const std::string& hname ) 
{
   m_h_detector = std::make_shared<TH1D>();
   h->Copy( *m_h_detector );

   const int Nbinsx = m_h_detector->GetNbinsX();
   m_v_detector = std::make_shared<TMatrixD>( Nbinsx, 1, m_h_detector->GetArray(), "D" );
}

void Sample::SetNominalResponse( const TH1 * h, const std::string& hname ) 
{ 
   m_h_response = std::make_shared<TH2D>();
   h->Copy( *m_h_response );

   const int Nbinsx = m_h_response->GetNbinsX();
   const int Nbinsy = m_h_response->GetNbinsY();

   m_M_response = std::make_shared<TMatrixD>( Nbinsx, Nbinsy, m_h_response->GetArray(), "D" );
}

void Sample::SetNominalTruth( const TH1 * h, const std::string& hname )   
{
   m_h_truth = std::make_shared<TH1D>();
   h->Copy( *m_h_truth );

   const int Nbinsx = m_h_truth->GetNbinsX();
   m_v_truth  = std::make_shared<TMatrixD>( Nbinsx, 1, m_h_truth->GetArray(), "D" );
}
