#ifndef __SAMPLE_H__
#define __SAMPLE_H__

#include <string>
#include <map>
#include <memory>
#include <iostream>

#include <TObject.h>
#include <TNamed.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TMatrixD.h>

typedef std::shared_ptr<TH1>  pTH1_t;
typedef std::shared_ptr<TH1D> pTH1F_t;
typedef std::shared_ptr<TH2D> pTH2F_t;
typedef std::shared_ptr<TH1D> pTH1D_t;
typedef	std::shared_ptr<TH2D> pTH2D_t;
typedef std::shared_ptr<TMatrixD> pTMatrixD_t;

enum SAMPLE_TYPE { kData = 0, kSignal = 1, kBackground = 2, kDataDriven = 3, kNSampleTypes = 4 };

class Sample : public TObject
{
 public:
 
   Sample( const std::string& name = "AnySample", const SAMPLE_TYPE type = SAMPLE_TYPE::kBackground, const std::string& latex = "Any sample you like" );
   ~Sample();

   void SetName( const std::string& name )  { m_name  = name;    };
   void SetLatex( const std::string& tex )  { m_latex = tex;     };
   void SetType( SAMPLE_TYPE type )   { m_type      = type;      };
   void SetIndex( int index )         { m_index     = index;     };

   void SetColor( int color )         { m_color     = color;     };
   void SetFillStyle( int fillstyle ) { m_fillstyle = fillstyle; };
   void SetLineStyle( int linestyle ) { m_linestyle = linestyle; };

   SAMPLE_TYPE GetType() { return m_type; };
   std::string& GetName() { return this->m_name; };
   int GetIndex()       { return m_index; };
   int GetColor()       { return m_color; };
   int GetFillStyle()   { return m_fillstyle; };
   int GetLineStyle()   { return m_linestyle; };

   void    SetDetector( const TH1 * h, const std::string& syst_name = "nominal", const std::string& hname = "detector" );
   void    SetDetector( pTH1D_t     h, const std::string& syst_name = "nominal", const std::string& hname = "detector" );
   pTH1D_t GetDetector( const std::string& syst_name = "nominal" );

   void	   SetResponse( const TH1 * h, const std::string& syst_name = "nominal", const std::string& hname = "response" );
   void    SetResponse( pTH2D_t     h, const std::string& syst_name = "nominal", const std::string& hname = "response" );
   pTH2D_t GetResponse( const std::string& syst_name = "nominal" );

   void	   SetTruth( const TH1 * h, const std::string& syst_name = "nominal", const std::string& hname = "truth" );
   void    SetTruth( pTH1D_t     h, const std::string& syst_name = "nominal", const std::string& hname = "truth" );
   pTH1D_t GetTruth( const std::string& syst_name = "nominal" );

   void    CalculateAcceptance( const std::string& syst_name = "nominal" );
   pTH1D_t GetAcceptance( const std::string& syst_name = "nominal" );

   void    CalculateEfficiency( const std::string& syst_name = "nominal" );
   pTH1D_t GetEfficiency( const std::string& syst_name = "nominal" );

   ClassDef( Sample, 1 )

 protected:
   std::string m_name;
   std::string m_latex;
   int m_index;
   int m_color;
   int m_linestyle;
   int m_fillstyle;
   SAMPLE_TYPE m_type;

   std::map< const std::string, pTH1D_t >      m_h_detector;
   std::map< const std::string, pTH2D_t >      m_h_response; 
   std::map< const std::string, pTH1D_t >      m_h_truth;
   std::map< const std::string, pTH1D_t >      m_h_acceptance;
   std::map< const std::string, pTH1D_t >      m_h_efficiency;
};

typedef std::shared_ptr<Sample>                  pSample_t;
typedef std::map< const std::string, pSample_t > SampleCollection_t;
typedef SampleCollection_t::iterator             SampleCollection_itr_t;
#endif /** __SAMPLE_H__ */
