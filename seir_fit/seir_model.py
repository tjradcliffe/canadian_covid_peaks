from ark4 import RungeKutta
from simple_minimizer import *

from datetime import datetime
import math
import sys

"""
Solves Susceptible/Exposed/Infectious/Recovered/Susceptible model equations.

The equations are, where [X]{d:0=>t} is the integral of X over d from 0 to t. Rather
than writing the equations in terms of various derivatives, I've focused entirely on
the number of susceptible people at various lagged times, and the probability of
transition through the different stages.

1) dE/dt = S*n*P_i - [(S(t-d)*n*P_i)*p_ei(d)]{d:0=>t} 
             = S*n*(I/N)*p_i - [(S(t-d)*n*(I/N)*p_i)*p_ei(d)]{d:0=>t}

2) dI/dt = [S(t-d)*n*(I/N)*p_i*p_ei(d)]{d:0=>t} - [(S(t-d)*n*(I/N)*p_i)*p_ir(d)]{d:0=>t}

3) dR/dt = [(S(t-d)*n*(I/N)*p_i*p_ir(d)]{d:0=>t} - [(S(t-d)*n*(I/N)*p_i)*p_rs(d)]{d:0=>t}

4) dS/dt = - S*n*(I/N)*p_i

where:

N = total population
E = number of  people exposed
S = number of poeple susceptible
I = number of people infectious
R = number of people recovered

and:

n = number of encounters between people each day
P_i = probablity an encounter will lead to infection = (I/N)*p_i
I/N = fraction of population that is infectious
p_i = probability an encounter with an infectious person will result in infection

p_ei(T) = probability distribution that a person who was exposed time T
                ago transtitions to the infectious state now
                
p_er(T) = probability distribution that person who was exposed time T
                ago transitions to recovered state now

The simplest forms of these distributions are just delta(t-T), so all people who
became exposed/infectious T ago now become infectious/recovered (different
T's for the two cases, in general). This is the focus here, with the assumption 
that we only care about day-scale changes, so the integrals just become:

S(t-d)*n*(I/N)*p_i*delta(t-T_ei) = S(t-T_ei)*n*(I/N)*p_i

and so on.

NOTE that the probability distributions are all from the time of exposure, not
the time of the current state's onset. The relevant distribution can be generated
from the individual-state distributions by composition, but I'm going to argue for
measurement from exposure to the final result of the disease. Note also that in
this model so far there is no death rate. There should be.

The parameters are fixed by prior knowledge as follows:

n = 20 (doi:10.1016/j.socnet.2007.04.005). For 18-55 21 is appropriate, for
1-5 12, for 6-18 14, and for Y > 55 it's about 21-2*(Y-55)/3. I'm modelling a 
single population for now, so 16 will do.

p_i = free parameter. Fit this to data.

p_es(T) = delta(T-T_rs), T_rs = free parameter, fit to the data

p_ei(T) = delta(T-T_ei), T_ei = 3 days (from exposure to infectious)
p_er(T) = delta(T-T_ir), T_ir = 10 days (from exposure to recovery => 7 days infectious)

both values from: https://www.health.com/news/omicron-timeline

Ranges are large, though, and the range for the infectious period may matter a
lot. For the first model, just keep the single number.

In the following equations lstY = [E, I, R, S] and each equation returns the relevant
derivative.
"""

class ExposedEquation:
    """
    dE/dt = S*n*(I/N)*p_i - [(S(t-d)*n*(I/N)*p_i)*p_ei(d)]{d:0=>t}
             = S*K - [(S(t-d)*K)*p_ei(d)]{d:0=>t}, K = n*(I/N)*p_i
    fP = nEncounterRate*fInfectionProbabilityPerEncounter
    """
    
    def __init__(self, fTei, fFactor, pHistory):
        # Factor = EncounterRate*InfectionProbabilityPerEncounter/Population
        # Units of encouter rate determine units of all derivatives => per day for this model
        self.fTei = fTei
        self.fFactor = fFactor
        self.pHistory = pHistory
        
    def __call__(self, fT, lstY):
        fExposed, fInfectious, fRecovered, fSusceptible = lstY

        fK = fInfectious*self.fFactor # (I/N)*EncounterRate*InfectionProbabilityPerEncounter
        fDEdt = fSusceptible*fK
        nIndex = int(fT-self.fTei) # look back Tei days ago
        if nIndex >= 0 and nIndex < len(self.pHistory.lstInfectious):
            fK = self.pHistory.lstInfectious[nIndex]*self.fFactor
            fDEdt -= self.pHistory.lstSusceptible[nIndex]*fK # previously exposed, now infectious
            
        return fDEdt

class InfectiousEquation:
    """
    2) dI/dt = [S(t-d)*n*(I/N)*p_i*p_ei(d)]{d:0=>t} - [(S(t-d)*n*(I/N)*p_i)*p_ir(d)]{d:0=>t}
                = [S(t-d)*K*p_ei(d)]{d:0=>t} - [(S(t-d)*K)*p_ir(d)]{d:0=>t}, K = n*(I(t-d)/N)*p_i
    """
    
    def __init__(self, fTei, fTer, fFactor, pHistory):
        # Factor = EncounterRate*InfectionProbabilityPerEncounter/Population
        self.fTei = fTei
        self.fTer = fTer
        self.fFactor = fFactor
        self.pHistory = pHistory # used to communicate with reporter keeping track of results
        
    def __call__(self, fT, lstY):
        fExposed, fInfectious, fRecovered, fSusceptible = lstY
        
        fDIdt = 0.0
        nIndex = int(fT-self.fTei)
        if nIndex >= 0 and nIndex < len(self.pHistory.lstInfectious):
            fK = self.pHistory.lstInfectious[nIndex]*self.fFactor # (I/N)*EncounterRate*InfectionProbabilityPerEncounter
            fDIdt = self.pHistory.lstSusceptible[nIndex]*fK # newly converted from exposed

        nIndex = int(fT-self.fTer)        
        if nIndex >= 0:
            fK = self.pHistory.lstInfectious[nIndex]*self.fFactor # (I/N)*EncounterRate*InfectionProbabilityPerEncounter
            fDIdt -= self.pHistory.lstSusceptible[nIndex]*fK # newly recovered

        return fDIdt

class RecoveredEquation:
    """
    3) dR/dt = [(S(t-d)*n*(I/N)*p_i*p_ir(d)]{d:0=>t}  
                  = [S(t-d)*K*p_ir(d)]{d:0=>t}, K = n*(I(t-d)/N)*p_i
    
    """
    def __init__(self, fTer, fFactor, pHistory):
        # Factor = EncounterRate*InfectionProbabilityPerEncounter/Population
        self.fTer = fTer
        self.fFactor = fFactor
        self.pHistory = pHistory
        
    def __call__(self, fT, lstY):
        fExposed, fInfectious, fRecovered, fSusceptible = lstY
        
        fDRdt = 0.0
        nIndex = int(fT-self.fTer)
        if nIndex >= 0:
            fK = self.pHistory.lstInfectious[nIndex]*self.fFactor # (I/N)*EncounterRate*InfectionProbabilityPerEncounter
            fDRdt = self.pHistory.lstSusceptible[nIndex]*fK # newly recovered

        return fDRdt

class SusceptibleEquation:
    """
    4) dS/dt = - S*n*(I/N)*p_i
    """
    def __init__(self, fFactor, pHistory):
        # Factor = EncounterRate*InfectionProbabilityPerEncounter/Population
        self.fFactor = fFactor
        self.pHistory = pHistory

    def __call__(self, fT, lstY):
        fExposed, fInfectious, fRecovered, fSusceptible = lstY
        
        fK = fInfectious*self.fFactor # (I/N)*EncounterRate*InfectionProbabilityPerEncounter
        fDSdt = -fSusceptible*fK # number who become exposed
        
        return fDSdt

class History:
    """Keeps track of the history of the simulation, one day at a time"""
    
    def __init__(self):
        self.lstSusceptible = []
        self.lstExposed = []
        self.lstInfectious = []
        self.lstRecovered = []

    def __call__(self, fT, pSolver, bEndpoint):
        
        fExposed, fInfectious, fRecovered, fSusceptible = pSolver.getValues()
        
        self.lstSusceptible.append(fSusceptible)
        self.lstExposed.append(fExposed)
        self.lstInfectious.append(fInfectious)
        self.lstRecovered.append(fRecovered)

### MODEL PARAMETERS 

# simulation parameters
fPopulation = 38E6 # Canada

# Fixed parameters: these are set by the things we know about covid
fEncounterRate = 20 # per day. This sets rate scales for whole simulation as "per day"

# minimization parameters (based on average of first 9 peaks)
fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer = 0.00256, 0.00968, 2.888, 10.056

# Run the SEIR model for a given set of parameters and return the history
def SEIRModel(fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer, nDays = 1400):
        
        # convenience factor describing infection probability per infected person
        fFactor = fEncounterRate*fInfectionProbabilityPerEncounter/fPopulation
        
        fInfectious = 1.0 # set up solver with 1 infectious person
        fTimeStep = 1.0 # days
        pSolver = RungeKutta(nDays, fTimeStep)
        pHistory = History() # define here so equatins can have access to it
        pSolver.addEquation(ExposedEquation(fTei, fFactor, pHistory), 0.0) # nobody in "exposed" state yet
        pSolver.addEquation(InfectiousEquation(fTei, fTer, fFactor, pHistory), fInfectious) # start with one infectious person
        pSolver.addEquation(RecoveredEquation(fTer, fFactor, pHistory), 0.0) # nobody recovered yet
        pSolver.addEquation(SusceptibleEquation(fFactor, pHistory), fPopulation-fInfectious) # all but one
        pSolver.addAuxFunction(pHistory)
        
        pSolver.evolve(False) # run the model

        lstHospitalized = [fFractionHospitalized*fX for fX in pHistory.lstInfectious]

        return pHistory, lstHospitalized
        
class SEIRModelObjective:
    """Finds RMS error between aligned peak data and SEIR model
    output. Alignment is done on max values"""
    
    def __init__(self, lstPeakData):
        """Peak data is single peak from Gaussian decomposition"""
        self.lstPeakData = lstPeakData
        fMax = max(self.lstPeakData)
        self.nMaxIndex = self.lstPeakData.index(fMax)        
 #       print("MAX: ", fMax, self.nMaxIndex)
        self.nOffset = 0
        
    def __call__(self, lstParams):
        fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer  = lstParams

        pHistory, lstHospitalized = SEIRModel(fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer)
        nMaxIndex = lstHospitalized.index(max(lstHospitalized)) # first instance, but should be OK
        self.nOffset = self.nMaxIndex - nMaxIndex
#        print("OFFSET: ", self.nOffset, self.nMaxIndex, nMaxIndex)
                
        fRMS = 0.0
        nCount = 0
        for nI, fData in enumerate(lstHospitalized):
            nIndex = nI+self.nOffset
            if nIndex >= 0 and nIndex < len(self.lstPeakData):
                fRMS += (self.lstPeakData[nI+self.nOffset]-fData)**2
                nCount += 1
        fRMS = math.sqrt(fRMS/nCount)
        
        return fRMS

if __name__ == "__main__":
    
    nPeak = -1 # first omicron
    if len(sys.argv) > 1:
        nPeak = int(sys.argv[1])

    if nPeak < 0:
        bLoop = True
        nPeak = 1
        strInputFile = "can_hosp_patients_fit.csv"
        strHeader = open(strInputFile).readline()
        nPeakMax = nPeak+(len(strHeader.strip().split())-1)//3
    else:
        nPeakMax = nPeak+1

    print("# Peak FracHosp InfectProb Tei Ter RMSError")
    for nColumn in range(nPeak+2, nPeakMax+2):
        
        strInputFile = "can_hosp_patients_fit.csv"
        lstPeakData = []
        with open(strInputFile) as inFile:
            for strLine in inFile:
                if strLine.strip().startswith("#"): continue
                nPatients = int(float(strLine.strip().split()[nColumn]))
                lstPeakData.append(nPatients)

        # RMS error
        pObjective = SEIRModelObjective(lstPeakData)

        if len(sys.argv) > 3: # command line arguments present so use them
            fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer  = list(map(float, sys.argv[2:]))
        else:
            # build the minimizer 
            lstOrder = [0, 1, -1, -1]
            pMinimizer = SimpleMinimizer(4)
            pMinimizer.setStarts([fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer])
            pMinimizer.setOrder(lstOrder)
            lstScales = [0.001, 0.005, 0.5, 0.5]
            pMinimizer.setScales(lstScales)
            pMinimizer.setObjective(pObjective)
            nCount, pFinal, nReason = pMinimizer.minimize()
#            print("Minimization report: ", pMinimizer.getConvergenceReason(nReason))
            lstParams = pFinal.getVertex()
            fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer = lstParams
            
        pHistory, lstHospitalized = SEIRModel(fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer)
        print(str(nColumn-2), " ".join(map(str, lstParams)), pObjective([fFractionHospitalized, fInfectionProbabilityPerEncounter, fTei, fTer]))

        with open("seir_model_fit_"+str(nColumn-2)+".csv", "w") as outFile:
            outFile.write("# fFractionHospitalized, fDayOffset, fInfectionProbabilityPerEncounter, fTei, fTer\n")
            outFile.write("# "+" ".join(map(str, ([fFractionHospitalized, pObjective.nOffset, fInfectionProbabilityPerEncounter, fTei, fTer])))+"\n")
            outFile.write("# Tei/r = days from exposure to infectious/recovered\n")
            outFile.write("# Day 0 = 2020-01-23\n")
            outFile.write("# Day Susceptible Exposed Infectious Recovered Fit Data\n")
            for nI, fHospitalized in enumerate(lstHospitalized):
                nDataIndex = nI+pObjective.nOffset
                if nDataIndex > -1 and nDataIndex < len(lstPeakData):
                    outFile.write(str(nI+pObjective.nOffset)+" "+str(pHistory.lstSusceptible[nI])+" "+str(pHistory.lstExposed[nI])+" "+str(pHistory.lstInfectious[nI])+" "+str(pHistory.lstRecovered[nI])+" "+str(fHospitalized)+" "+str(lstPeakData[nDataIndex])+"\n ")
                else:
                    outFile.write(str(nI+pObjective.nOffset)+" "+str(pHistory.lstSusceptible[nI])+" "+str(pHistory.lstExposed[nI])+" "+str(pHistory.lstInfectious[nI])+" "+str(pHistory.lstRecovered[nI])+" "+str(fHospitalized)+" 0\n ")
