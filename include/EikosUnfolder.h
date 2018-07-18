#ifndef __EikosUnfolder_H__
#define __EikosUnfolder_H__

#include <TObject.h>
#include <TH1D.h>
#include <TMath.h>
#include <TRandom3.h>

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
#include <iomanip>

#include "Sample.h"

typedef std::pair< std::string, std::string >  SystPair_t;
typedef std::pair< std::vector<double>, std::vector<double> > SystValues_t;

enum REGULARIZATION  { kUnregularized = 0, kCurvature = 1,  kMultinormal = 2 };
enum PRIOR_SHAPE     { kPriorFlat = 0, kPriorGauss = 1, kPriorGamma = 2 };         
enum SYSTEMATIC_TYPE { kDetector = 0, kModelling = 1, kDataDriven = 3 }; 
enum RUN_STAGE       { kStageEstimatePrior, kStageStatSyst, kStageStatOnly, kStageTableOfSyst }; 

//enum StatusCode { kSuccess = 0, kWarning = 1, kError = 2 };

/////////////////////////////////

//namespace Eikos {

class EikosUnfolder : public BCModel, public TObject
{
 public:
    EikosUnfolder();
    ~EikosUnfolder();

    void SetRegularization( REGULARIZATION r )   { m_regularization = r; };
    void SetPriorShape( PRIOR_SHAPE s = kPriorFlat );

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
    void SetSystematicType( const std::string& sname, SYSTEMATIC_TYPE type );
    void SetSystematicType( int index, SYSTEMATIC_TYPE type );
    SYSTEMATIC_TYPE GetSystematicType( int index ) const;
    SYSTEMATIC_TYPE GetSystematicType( const std::string& sname ) const;

    void    SetData( const TH1 * data );
    pTH1D_t GetData() { return m_h_data; };

    void    SetPrior( const TH1 * h );
    void    SetPrior( pTH1D_t h );
    pTH1D_t GetPrior() { return m_h_prior; };

    void   SetLuminosity( double lumi ) { m_lumi = lumi; };
    double GetLuminosity()              { return m_lumi; };

    void PrepareForRun( RUN_STAGE run_stage );

    pTH1D_t GetDiffxsAbs( const std::string hname = "diffxs_abs" );
    pTH1D_t GetDiffxsRel( const std::string hname = "diffxs_rel" );
    pTH1D_t GetSystematicsPullHistogram();

//    virtual double LogAPrioriProbability(const std::vector<double>& parameters );
    virtual double LogLikelihood( const std::vector<double>& parameters );
//    virtual double LogProbability( const std::vector<double>& parameters );
    virtual void CalculateObservables(const std::vector<double>& parameters);
    virtual void MCMCUserIterationInterface();

    ClassDef( EikosUnfolder, 1 )

 protected:
    void PrepareSystematics();
   
    pTH1D_t MakeTruthHistogram( const std::vector<double>& parameters );

    pTH1D_t MakeFoldedHistogram( pTH1D_t p_h, const std::string& syst_name="nominal", const std::string& hname = "folded" );
    pTH1D_t MakeFoldedHistogram( const std::vector<double>& parameters, const std::string& syst_name="nominal", const std::string& hname = "folded" );

 //~~~~~~~~~~~~~~~~~~~~~

 protected:
//    TRandom3    m_rng;

    std::string m_name;
    int         m_nbins;
    std::vector<double> m_parameters;

    REGULARIZATION      m_regularization;
    PRIOR_SHAPE         m_prior_shape;
    RUN_STAGE           m_runStage;
    bool                m_syst_initialized;
    bool                m_obs_initialized;
    double              m_lumi;
    std::vector<double> m_xedges;
    std::vector<double>	m_bw;

    SampleCollection_t                     m_samples;
    std::map< const std::string, int >     m_samples_index;
    std::string m_signal_sample;
 
    std::map< const std::string, int >           m_syst_index;
    std::vector<std::string>                     m_syst_names;
    std::vector<SystPair_t>                      m_syst_pairs;
    std::vector<SystValues_t>                    m_syst_values;
    std::vector<SYSTEMATIC_TYPE>                 m_syst_types;

    pTH1D_t   m_h_data;
    pTH1D_t   m_h_prior; 
};

//} // namespace Eikos

#endif /** __EikosUnfolder_H__ */
