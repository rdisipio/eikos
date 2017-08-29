#ifndef __EikosUnfolder_H__
#define __EikosUnfolder_H__

#include <TObject.h>
#include <TH1D.h>

#include <BAT/BCModel.h>
#include <BAT/BCMTFSystematic.h>
#include <BAT/BCMTFSystematicVariation.h>
#include <BAT/BCMTFTemplate.h>
#include <BAT/BCMath.h>

#include <iostream>
#include <map>

#include "Sample.h"

//enum StatusCode { kSuccess = 0, kWarning = 1, kError = 2 };

/////////////////////////////////

//namespace Eikos {

class EikosUnfolder : public BCModel, public TObject
{
 public:
    EikosUnfolder();
    ~EikosUnfolder();

    inline size_t GetNSamples()       { return m_samples.size(); };
    inline size_t GetNSystematics()   { return m_systematics.size(); };

    int GetSampleIndex( const std::string& name );
    int GetSystematicIndex( const std::string& name );

    int AddSample( const std::string& name, const std::string& latex = "Sample", SAMPLE_TYPE type = SAMPLE_TYPE::kSignal, int color = -1, int fillstyle = -1, int linestyle = -1 );
    void SetSignalSample( Sample * signal )       { m_signal_sample = signal; };
    Sample * GetSample( const std::string& name ) { return m_samples[name]; };
    Sample * GetSignalSample() { return m_signal_sample; };

    int AddSystematic( const std::string& sname, double min, double max, const std::string & latexname = "", const std::string & unitstring = ""  );
    int AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, const TH1D * h_u, const TH1D * h_d, const TH1D * h_n = NULL );
    int AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, double k_u, double k_d, const TH1D * h_n = NULL );

    void SetData( const TH1 * data );
    TH1D * GetData() { return m_h_data; };

    void PrepareForRun();

    double LogLikelihood( const std::vector<double>& parameters );
//    void MCMCUserIterationinterface();

    ClassDef( EikosUnfolder, 1 )

 protected:
    double ExpectationValue( int r );

 //~~~~~~~~~~~~~~~~~~~~~

 protected:
    std::string m_name;
    int         m_nbins;
    std::vector<double> m_parameters;

    std::vector<double> m_xedges;
    std::vector<double>	m_bw;

    SampleCollection_t                     m_samples;
    std::map< const std::string, int >     m_samples_index;
    Sample * m_signal_sample;
 
    std::vector< BCMTFSystematic * >       m_systematics;
    std::map< const std::string, int >     m_systematics_index;

    TH1D * m_h_data;
};

//} // namespace Eikos

#endif /** __EikosUnfolder_H__ */
