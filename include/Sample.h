#ifndef __SAMPLE_H__
#define __SAMPLE_H__

#include <string>
#include <map>
#include <memory>

#include <TObject.h>
#include <TNamed.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TMatrixD.h>

typedef std::shared_ptr<TH1>  pTH1_t;
typedef std::shared_ptr<TH1D> pTH1D_t;
typedef	std::shared_ptr<TH2D> pTH2D_t;
typedef std::shared_ptr<TMatrixD> pTMatrixD_t;

enum SAMPLE_TYPE { kData = 0, kSignal = 1, kBackground = 2, kDataDriven = 3, kNSampleTypes = 4 };

class Sample : public TObject
{
 public:
 
   Sample( const std::string& name = "AnySample" );
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

   void SetNominalDetector( const TH1 * h, const std::string& hname = "detector" );
   inline pTH1D_t     GetNominalDetector_histogram()         { return m_h_detector; };
   inline pTMatrixD_t GetNominalDetector_vector()        { return m_v_detector; };

   void	SetNominalResponse( const TH1 * h, const std::string& hname = "response" );
   inline pTH2D_t     GetNominalResponse_histogram()     { return m_h_response; };
   inline pTMatrixD_t GetNominalResponse_matrix()        { return m_M_response; };

   void	SetNominalTruth( const TH1 * h, const std::string& hname = "truth" );
   inline pTH1D_t     GetNominalTruth_histogram()      { return	m_h_truth; };
   inline pTMatrixD_t GetNominalTruth_vector()         { return m_v_truth; };

   ClassDef( Sample, 1 )

 protected:
   std::string m_name;
   std::string m_latex;
   int m_index;
   int m_color;
   int m_linestyle;
   int m_fillstyle;
   SAMPLE_TYPE m_type;

   pTH1D_t m_h_detector;
   pTH2D_t m_h_response;
   pTH1D_t m_h_truth;

   pTMatrixD_t m_v_detector;
   pTMatrixD_t m_M_response;
   pTMatrixD_t m_v_truth;

};

typedef std::shared_ptr<Sample>                  pSample_t;
typedef std::map< const std::string, pSample_t > SampleCollection_t;
typedef SampleCollection_t::iterator             SampleCollection_itr_t;
#endif /** __SAMPLE_H__ */
