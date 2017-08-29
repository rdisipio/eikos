#ifndef __SAMPLE_H__
#define __SAMPLE_H__

#include <string>
#include <map>

#include <TObject.h>
#include <TNamed.h>
#include <TH1D.h>
#include <TH2D.h>

enum SAMPLE_TYPE { kData = 0, kSignal = 1, kBackground = 2, kDataDriven = 3, kNSampleTypes = 4 };

class Sample : public TObject
{
 public:
 
   Sample( const std::string& name = "AnySample" );
   ~Sample();

   void SetName( const std::string& name )  { m_name      = name;      };
   void SetLatex( const std::string& tex )  { m_latex      = tex;      };
   void SetType( SAMPLE_TYPE type )   { m_type      = type;      };
   void SetIndex( int index )         { m_index     = index;     };

   void SetColor( int color )         { m_color     = color;     };
   void SetFillStyle( int fillstyle ) { m_fillstyle = fillstyle; };
   void SetLineStyle( int linestyle ) { m_linestyle = linestyle; };

   SAMPLE_TYPE GetType() { return m_type; };
   int GetIndex()       { return m_index; };
   int GetColor()       { return m_color; };
   int GetFillStyle()   { return m_fillstyle; };
   int GetLineStyle()   { return m_linestyle; };

   void SetNominalHistogramDetector( TH1D * h ) { m_h_detector = (TH1D*)h->Clone(); };
   TH1D * GetNominalHistogramDetector()         { return m_h_detector;       };

   void	SetNominalHistogramResponse( TH2D * h ) { m_h_response = (TH2D*)h->Clone(); };
   TH2D * GetNominalHistogramResponse()         { return m_h_response;       };

   void	SetNominalHistogramTruth( TH1D * h )   { m_h_truth = (TH1D*)h->Clone();    };
   TH1D * GetNominalHistogramTruth() 	       { return	m_h_truth;  	    };

   ClassDef( Sample, 1 )

 protected:
   std::string m_name;
   std::string m_latex;
   int m_index;
   int m_color;
   int m_linestyle;
   int m_fillstyle;
   SAMPLE_TYPE m_type;

   TH1D * m_h_detector;
   TH2D * m_h_response;
   TH1D * m_h_truth;
};

typedef std::map< const std::string, Sample * > SampleCollection_t;
typedef SampleCollection_t::iterator            SampleCollection_itr_t;
#endif /** __SAMPLE_H__ */
