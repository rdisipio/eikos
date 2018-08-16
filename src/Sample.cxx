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
   p_h->SetName( hname.c_str() );
   SetDetector( p_h, syst_name, hname );
}

void Sample::SetDetector( pTH1D_t h, const std::string& syst_name, const std::string& hname )
{
   m_h_detector[syst_name] = std::make_shared<TH1D>();
   h->Copy( (*m_h_detector[syst_name]) );
   m_h_detector[syst_name]->SetName( hname.c_str() );
}

pTH1D_t Sample::GetDetector( const std::string& syst_name )  
{ 
  if( m_h_detector.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no detector histogram set for systematic " << syst_name << std::endl;
     throw std::runtime_error( "no detector histogram set" );
  }

  return m_h_detector[syst_name]; 
}

//////////////////////////////////////////

void Sample::SetResponse( const TH1 * h, const std::string& syst_name, const std::string& hname ) 
{ 
   m_h_response[syst_name] = std::make_shared<TH2D>();
   h->Copy( (*m_h_response[syst_name]) );
   m_h_response[syst_name]->SetName( hname.c_str() );
}

void Sample::SetResponse( pTH2D_t h, const std::string& syst_name, const std::string& hname )
{
   m_h_response[syst_name] = std::make_shared<TH2D>();
   h->Copy( (*m_h_response[syst_name]) );
   m_h_response[syst_name]->SetName( hname.c_str() );
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

void Sample::SetTruth( pTH1D_t h, const std::string& syst_name, const std::string& hname )
{
   m_h_truth[syst_name] = std::make_shared<TH1D>();
   h->Copy( (*m_h_truth[syst_name]) );
   m_h_truth[syst_name]->SetName( hname.c_str() );

   std::cout << "DEBUG: Set truth histogram for syst " << syst_name << " name = " << hname << std::endl; 
}

void Sample::SetTruth( const TH1 * h, const std::string& syst_name, const std::string& hname )   
{
   pTH1D_t p_h = std::make_shared<TH1D>();
   h->Copy( *p_h );
   SetTruth( p_h, syst_name, hname );
}

pTH1D_t Sample::GetTruth( const std::string& syst_name )
{
//  return m_h_truth.at( syst_name );

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

   std::string hname = std::string("acceptance_") + syst_name;
   TH1D * h_acc = (TH1D*)h_resp->ProjectionX( hname.c_str() );
   h_acc->Divide( h_acc, h_sig.get(), 1., 1., "B" );

   std::cout <<	"INFO: acceptance " << syst_name << ":"	<< std::endl;
   for(	int i =	0 ; i <	h_acc->GetNbinsX() ; ++i ) std::cout << std::setprecision(3) <<	h_acc->GetBinContent(i+1) << " ";
   std::cout <<	std::endl;

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

   std::string hname = std::string("efficiency_") + syst_name;
   TH1D	* h_eff	= (TH1D*)h_resp->ProjectionY( hname.c_str() );
   h_eff->Divide( h_eff, h_gen.get(), 1., 1., "B" );

   std::cout << "INFO: efficiency " << syst_name << ":" << std::endl;
   for( int i = 0 ; i < h_eff->GetNbinsX() ; ++i ) std::cout << std::setprecision(3) << h_eff->GetBinContent(i+1) << " ";
   std::cout << std::endl;

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

   std::string hname = std::string("migrations_") + syst_name;
   m_h_migrations[syst_name]->SetName( hname.c_str() );

   // normalize rows
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

/*
   // normalize columns
   for( int i = 0 ; i < h_resp->GetNbinsX() ; ++i ) { 
      double sumw = 0.;
      for( int j = 0 ; j < h_resp->GetNbinsY() ; ++j ) {
        sumw += h_resp->GetBinContent( i+1, j+1 );
      }

      for( int j = 0 ; j < h_resp->GetNbinsY() ; ++j ) {
         double z_old = h_resp->GetBinContent( i+1, j+1 );
         double z_new = ( sumw != 0. ) ? z_old / sumw : 0.;
         m_h_migrations[syst_name]->SetBinContent( i+1, j+1, z_new );
      }
   }
*/
}

pTH2D_t Sample::GetMigrations( const std::string& syst_name )
{
  if( m_h_migrations.count(syst_name) == 0 ) {
     std::cout << "ERROR: sample " << GetName() << " has no migrations histogram set for systematic " << syst_name << std::endl;
     return NULL;
  }

  return m_h_migrations[syst_name];
}

