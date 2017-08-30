#include "Sample.h"

ClassImp( Sample )

Sample::Sample( const std::string& name, const SAMPLE_TYPE type, const std::string& latex ) : 
  m_h_detector(NULL), m_h_response(NULL), m_h_truth(NULL)
{
  m_name      = name;
  m_latex     = latex;
  m_index     = -1;
  m_type      = type;
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
   m_v_detector = std::make_shared<TMatrixD>( Nbinsx, 1 );
   for( int i = 0 ; i < Nbinsx ; ++i ) (*m_v_detector)[i] = h->GetBinContent(i+1);
}

void Sample::SetNominalResponse( const TH1 * h, const std::string& hname ) 
{ 
   m_h_response = std::make_shared<TH2D>();
   h->Copy( *m_h_response );

   const int Nbinsx = m_h_response->GetNbinsX() + 1;
   const int Nbinsy = m_h_response->GetNbinsY() + 1;

   m_M_response = std::make_shared<TMatrixD>( Nbinsx, Nbinsy );
   for( int i = 0 ; i < Nbinsx ; ++i ) {
     for( int j = 0 ; j < Nbinsy ; ++j ) { 
       (*m_M_response)(i,j) = h->GetBinContent(i+1, j+1 );
     }
   }
}

void Sample::SetNominalTruth( const TH1 * h, const std::string& hname )   
{
   m_h_truth = std::make_shared<TH1D>();
   h->Copy( *m_h_truth );

   const int Nbinsx = m_h_truth->GetNbinsX() + 1;
   m_v_truth  = std::make_shared<TMatrixD>( Nbinsx, 1 );
   for( int i = 0 ; i < Nbinsx ; ++i ) (*m_v_truth)[i] = h->GetBinContent(i);
}
