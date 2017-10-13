#ifndef __EikosUnfolder_H__
#define __EikosUnfolder_H__

#include <TObject.h>
#include <TH1D.h>
#include <TMath.h>

#include <BAT/BCModel.h>
#include <BAT/BCGaussianPrior.h>
#include <BAT/BCPositiveDefinitePrior.h>
#include <BAT/BCMTFSystematic.h>
#include <BAT/BCMTFSystematicVariation.h>
#include <BAT/BCMTFTemplate.h>
#include <BAT/BCMath.h>

#include <iostream>
#include <map>
#include <algorithm>

#include "Sample.h"

typedef std::pair< std::string, std::string >  SystPair_t;

//enum StatusCode { kSuccess = 0, kWarning = 1, kError = 2 };

/////////////////////////////////

//namespace Eikos {

class EikosUnfolder : public BCModel, public TObject
{
 public:
    EikosUnfolder();
    ~EikosUnfolder();

    inline size_t GetNSamples()       { return m_samples.size(); };
    inline size_t GetNSystematics()   { return m_syst_index.size(); };

    int GetSampleIndex( const std::string& name );
    int GetSystematicIndex( const std::string& name );

    pSample_t AddSample( const pSample_t sample );
    pSample_t AddSample( const std::string& name, SAMPLE_TYPE type = SAMPLE_TYPE::kBackground, const std::string& latex = "Sample", int color = -1, int fillstyle = -1, int linestyle = -1 );
    void SetSignalSample( const std::string& name );
    pSample_t GetSample( const std::string& name ) { return m_samples.at(name); };
    pSample_t GetSignalSample();
    pSample_t GetBackgroundSample( const std::string& name = "background" );

    int AddSystematic( const std::string& sname, double min, double max, const std::string & latexname = "", const std::string & unitstring = ""  );
    void SetSystematicVariations( const std::string& sname, const std::string& var_u, const std::string& var_d );

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
    pTH1D_t MakeTruthHistogram( const std::vector<double>& parameters );
    pTH1D_t MakeFoldedHistogram( const std::vector<double>& parameters );

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
 
    std::map< const std::string, int >           m_syst_index;
    std::vector<std::string>                     m_syst_names;
    std::vector<SystPair_t>                      m_syst_pairs;

    pTH1D_t     m_h_data;
//    pTMatrixD_t m_v_data;
};

//} // namespace Eikos

#endif /** __EikosUnfolder_H__ */
