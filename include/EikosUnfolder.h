#ifndef __EikosUnfolder_H__
#define __EikosUnfolder_H__

#include <TObject.h>
#include <TH1D.h>

#include <BAT/BCModel.h>
#include <BAT/BCGaussianPrior.h>
#include <BAT/BCPositiveDefinitePrior.h>
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

    pSample_t AddSample( const pSample_t sample );
    pSample_t AddSample( const std::string& name, SAMPLE_TYPE type = SAMPLE_TYPE::kBackground, const std::string& latex = "Sample", int color = -1, int fillstyle = -1, int linestyle = -1 );
    void SetSignalSample( const std::string& name );
    pSample_t GetSample( const std::string& name ) { return m_samples.at(name); };
    pSample_t GetSignalSample();
    pSample_t GetBackgroundSample( const std::string& name = "background" );

    int AddSystematic( const std::string& sname, double min, double max, const std::string & latexname = "", const std::string & unitstring = ""  );
    int AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, const pTH1D_t h_u, const pTH1D_t h_d, const pTH1D_t h_n = NULL );
    int AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, double k_u, double k_d, const pTH1D_t h_n = NULL );

    void    SetData( const TH1 * data );
    pTH1D_t GetData() { return m_h_data; };

    void   SetLuminosity( double lumi ) { m_lumi = lumi; };
    double GetLuminosity()              { return m_lumi; };

    void PrepareForRun();

    pTH1D_t GetDiffxsAbs();

    double LogLikelihood( const std::vector<double>& parameters );
//    void MCMCUserIterationinterface();

    ClassDef( EikosUnfolder, 1 )

 protected:
    pTH1D_t MakeUnfolded( const std::vector<double>& parameters );

 //~~~~~~~~~~~~~~~~~~~~~

 protected:
    std::string m_name;
    int         m_nbins;
    std::vector<double> m_parameters;

    double              m_lumi;
    std::vector<double> m_xedges;
    std::vector<double>	m_bw;

    SampleCollection_t                     m_samples;
    std::map< const std::string, int >     m_samples_index;
    std::string m_signal_sample;
 
    std::vector< BCMTFSystematic * >       m_systematics;
    std::map< const std::string, int >     m_systematics_index;

    pTH1D_t     m_h_data;
    pTMatrixD_t m_v_data;
};

//} // namespace Eikos

#endif /** __EikosUnfolder_H__ */
