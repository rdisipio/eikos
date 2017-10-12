#include "Sample.h"

ClassImp( Sample )

Sample::Sample( const std::string& name, const SAMPLE_TYPE type, const std::string& latex ) 
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

void Sample::SetDetector( const TH1 * h, const std::string& syst_name, const std::string& hname ) 
{
   pTH1D_t p_h = std::make_shared<TH1D>();
   h->Copy( *p_h );
   SetDetector( p_h, syst_name, hname );
}

void Sample::SetDetector( pTH1D_t h, const std::string& syst_name, const std::string& hname )
{
   m_h_detector[syst_name] = std::make_shared<TH1D>();
   h->Copy( (*m_h_detector[syst_name]) );
}

pTH1D_t Sample::GetDetector( const std::string& syst_name )  
{ 
  if( m_h_detector.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no detector histogram set for systematic " << syst_name << std::endl;
     return NULL;
  }

//  h = m_h_detector[syst_name]; 
//  h->Print("all");
  return m_h_detector[syst_name]; 
}

//////////////////////////////////////////

void Sample::SetResponse( const TH1 * h, const std::string& syst_name, const std::string& hname ) 
{ 
   m_h_response[syst_name] = std::make_shared<TH2D>();
   h->Copy( (*m_h_response[syst_name]) );
}


pTH2D_t Sample::GetResponse( const std::string& syst_name )
{
  if( m_h_response.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no response matrix histogram set for systematic " << syst_name << std::endl;
     return NULL;
  }

  return m_h_response[syst_name];    
}

//////////////////////////////////////////

void Sample::SetTruth( const TH1 * h, const std::string& syst_name, const std::string& hname )   
{
   m_h_truth[syst_name] = std::make_shared<TH1D>();
   h->Copy( (*m_h_truth[syst_name]) );
}

pTH1D_t Sample::GetTruth( const std::string& syst_name )
{
  if( m_h_truth.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no truth histogram set for systematic " << syst_name << std::endl;
     return NULL;
  }

  return m_h_truth[syst_name];
}


//////////////////////////////////////////


void Sample::CalculateAcceptance( const std::string& syst_name )
{
   pTH2D_t h_resp = GetResponse( syst_name );
   pTH1D_t h_sig  = GetDetector( syst_name );

   TH1D * h_acc = (TH1D*)h_resp->ProjectionX( "acceptance" );
   h_acc->Divide( h_sig.get() );

   std::cout <<	"INFO: acceptance " << syst_name << ":"	<< std::endl;
   h_acc->Print("all");

   m_h_acceptance[syst_name] = std::make_shared<TH1D>();
   h_acc->Copy( *(m_h_acceptance[syst_name].get()) );
}


pTH1D_t Sample::GetAcceptance( const std::string& syst_name )
{
  if( m_h_acceptance.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no acceptance histogram set for systematic " << syst_name << std::endl;
     return NULL;
  }

  return m_h_acceptance[syst_name];
}


//////////////////////////////////////////


void Sample::CalculateEfficiency( const std::string& syst_name )
{
   pTH2D_t h_resp = GetResponse( syst_name );
   pTH1D_t h_gen  = GetTruth( syst_name );

   TH1D	* h_eff	= (TH1D*)h_resp->ProjectionY( "efficiency" );
   h_eff->Divide( h_gen.get() );

   std::cout << "INFO: efficiency " << syst_name << ":" << std::endl;
   h_eff->Print("all");

   m_h_efficiency[syst_name] = std::make_shared<TH1D>();
   h_eff->Copy( *(m_h_efficiency[syst_name].get()) );
}

pTH1D_t Sample::GetEfficiency( const std::string& syst_name )
{
  if( m_h_efficiency.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no efficiency histogram set for systematic " << syst_name << std::endl;
     return NULL;
  }

  return m_h_efficiency[syst_name];
}

//////////////////////////////////////////


void Sample::CalculateMigrations( const std::string& syst_name )
{
   m_h_migrations[syst_name] = std::make_shared<TH2D>();

   pTH2D_t h_resp = GetResponse( syst_name );
   h_resp->Copy( *(m_h_migrations[syst_name].get()) );

   // normalize rows (should become configurable)
   for(	int j = 0 ; j < h_resp->GetNbinsY() ; ++j ) {
      double sumw = 0.;

      for( int i = 0 ; i < h_resp->GetNbinsX() ; ++i ) {
        sumw += h_resp->GetBinContent( i+1, j+1 );
      }

      for( int i = 0 ; i < h_resp->GetNbinsX() ; ++i ) {
         double z_old = h_resp->GetBinContent( i+1, j+1 );
         double z_new = ( sumw != 0. ) ? z_old / sumw : 0.;
         m_h_migrations[syst_name]->SetBinContent( i+1, j+1, z_new ); 
      }

   }
}

pTH2D_t Sample::GetMigrations( const std::string& syst_name )
{
  if( m_h_migrations.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no migrations histogram set for systematic " << syst_name << std::endl;
     return NULL;
  }

  return m_h_migrations[syst_name];
}

