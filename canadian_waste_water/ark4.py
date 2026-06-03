
import math
import sys

"""
This class solves a set of ODEs using 4th order Runge Kutta with
adaptive step size.
  
To turn x'' + x = 0 into a system, we will imagine a vector with two
components, called Y. Now let the first component Y[0] = x and the second
component Y[1] = Y[0]' = x' .  Now rewrite the equation in terms of these
variables. It will be Y[1]' + Y[0] = 0. Solving for Y[1]' we get

  Y[1]' = -Y[0].

Now the vector Y' has compenents Y[0]' = Y[1] and Y[1]' = -Y[0] . These are
the equations we put in our equations.

The intial conditions are given as the values of the dependent variable
and its derivatives at time 0, so in the case above, the intial conditions
would be x(t=0) and x'(t=0).

Equations are added to the system with addEquation calls.  Each addEquation
call also requires a value for the next initial condition.  This is an easy
way of ensuring that enough initial conditions are supplied.

Equations must define __call__ with signature (fTime, vecY).  Each equation 
takes the full vector of Y-values and returns the first dirivative of 
the Y-value it is associated with.
"""
class RungeKutta:
    # constuctor sets up basic ranges
    def __init__(self, fTF=1.0, fStep=0.001, nIterations=1000, fAccuracy=0.001, fT0 = 0.0) :
        self.fT0 = fT0
        self.fTF = fTF 
        self.fTimeStep = fStep
        self.fFractionalAccuracy = fAccuracy
        self.nAdaptiveIterations = nIterations
        self.lstAuxFunction = []
        
        self.vecEquation = [] # system of 1st order ODEs to solve
        self.vecY = [] 		# vector of value and function derivatives
        self.vecW1 = []		# vector of temporary values used for interpolation
        self.vecW2 = []		# vector of temporary values used for interpolation
        self.vecW3 = []		# vector of temporary values used for interpolation
        self.vecW4 = []		# vector of temporary values used for interpolation
        self.vecQ = []		# vector of temporary values used for interpolation
        
    # evolve moves the solution forward one step at a time
    def evolve(self, bAdaptive = True):
        
        fT = self.fT0
        for pAuxFunction in self.lstAuxFunction:
            pAuxFunction(fT,self, True)			
        nHFactor = 2
        bNext = True
        while fT < self.fTF and bNext:
            # adaptive step-size control loop
            nAdaptCount = 0  		# number of step adaptions
            if nHFactor > 1:
                nHFactor -= 1 		# factor for step reduction
            fTimeStep = self.fTimeStep
            if fT + fTimeStep/nHFactor > self.fTF:	# force last point to end-time
                fTimeStep = nHFactor*(self.fTF-fT)
                bNext = False
            vecYStart = self.vecY  	# save starting point
            fDeltaMax = 0.0 		# error estimate based on halved steps
            vecYBig = [] 			# value/derivative at end of sub-step
            nHFactorStart = nHFactor	# save starting compression
            while True:
                self.vecY = vecYStart  # restore starting point
                vecYBig  = self.RK4(fT,fTimeStep,self.vecY,nHFactor)
                if not bAdaptive: # only take big steps
                    nHFactor += 1
                    break
                nNextFactor = 2*nHFactor
                vecYLowerHalf = self.RK4(fT,fTimeStep,self.vecY,nNextFactor)
                vecYUpperHalf = self.RK4(fT+self.fTimeStep/nNextFactor,fTimeStep, vecYLowerHalf, nNextFactor)

                nHFactor += 1
                nAdaptCount += 1
                if (nAdaptCount > self.nAdaptiveIterations):
                    print("Adapt Count Exceeded!")
                    sys.exit(-1)

                # get average error (assumes all scales equal,
                # or that only one dominates)
                fDeltaMax = 0.0
                for nIndex in range(0, len(self.vecY)):
                    if vecYBig[nIndex] == 0 and vecYUpperHalf[nIndex] == 0:
                        continue
                    fDiff = abs(vecYBig[nIndex]-vecYUpperHalf[nIndex])
                    fDelta = abs(0.5*fDiff/(vecYBig[nIndex]+vecYUpperHalf[nIndex]))
                    if fDeltaMax < fDelta:
                        fDeltaMax = fDelta

                if fDeltaMax <= self.fFractionalAccuracy:
                    break

            nHFactor -= 1 # undo effect of final increment
            if nHFactor != nHFactorStart:
                bNext = True

            self.vecY = vecYBig # transfer values
            for (nIndex, pEquation) in enumerate(self.vecEquation):
                pEquation.fY = self.vecY[nIndex]

            # increment loop time value
            fT += fTimeStep/nHFactor

            # call auxiliary functions
            for pAuxFunction in self.lstAuxFunction:
                pAuxFunction(fT, self,  not bNext)

    # add an equation to the system--ownership transfered
    def addEquation(self, pEquation, fInitial):
        self.vecEquation.append(pEquation)
        self.vecY.append(fInitial)
        self.vecW1.append(0.0)
        self.vecW2.append(0.0)
        self.vecW3.append(0.0)
        self.vecW4.append(0.0)
        self.vecQ.append(0.0)

    # set an auxiliary function
    def addAuxFunction(self, pAuxFunction):
        self.lstAuxFunction.append(pAuxFunction)
        
    # return the equations (modifiable!)
    def getEquations(self):
        return self.vecEquation

    # return the value and derivative array
    def getValues(self):
        return self.vecY

    def RK4(self, fT, fTimeStep, vecYin, nHFactor):
        
        vecY = list(vecYin)
        fH = fTimeStep/nHFactor;
        
        for nIndex in range(0, len(vecY)):
            self.vecW1[nIndex] = fH * self.vecEquation[nIndex](fT,vecY)
        for nIndex in range(0, len(vecY)):
            self.vecQ[nIndex] = vecY[nIndex] + 0.5*self.vecW1[nIndex]
            
        for nIndex in range(0, len(vecY)):
            self.vecW2[nIndex] = fH * self.vecEquation[nIndex](fT + 0.5*fH,self.vecQ)
        for nIndex in range(0, len(vecY)):
            self.vecQ[nIndex] = vecY[nIndex] + 0.5*self.vecW2[nIndex]
            
        for nIndex in range(0, len(vecY)):
            self.vecW3[nIndex] = fH * self.vecEquation[nIndex](fT + 0.5*fH,self.vecQ)
        for nIndex in range(0, len(vecY)):
            self.vecQ[nIndex] = vecY[nIndex] + self.vecW3[nIndex]
            
        for nIndex in range(0, len(vecY)):
            self.vecW4[nIndex] = fH * self.vecEquation[nIndex](fT + fH,self.vecQ)
        for nIndex in range(0, len(vecY)):
            vecY[nIndex] += 0.16666666666666666666666666666666666666*(
                    self.vecW1[nIndex] + 2*self.vecW2[nIndex] +
                        2*self.vecW3[nIndex] + self.vecW4[nIndex])

        return vecY

nTest = 1
if __name__ == "__main__" and nTest == 0:

    class Displacement:
        def __call__(self, fTime, vecY):
            return vecY[1]
            
    class Acceleration:
        def __call__(self, fTime, vecY):
            return -vecY[0]

    pSolver = RungeKutta(10, 0.5)
    pSolver.addEquation(Displacement(), 1.0)
    pSolver.addEquation(Acceleration(), 0.0)
            
    class Output(object):
        
        def __init__(self, strFilename):
            self.outFile = open(strFilename, "w")
            
        def __call__(self, fTime, pSolver, bFinal):
            self.outFile.write(str(fTime))
            for fValue in pSolver.vecY:
                self.outFile.write(","+str(fValue))
            self.outFile.write("\n")

    pOutput = Output("spring1.dat")
    pSolver.addAuxFunction(pOutput)
    
    pSolver.evolve()    # solve
    
    pOutput.outFile.close()

    strSpring1 = "0.0,1.0,0.0:\
0.5,0.8776041666666666,-0.47916666666666663:\
1.0,0.54058837890625,-0.8410373263888888:\
1.5,0.07142556155169455,-0.9971297935203269:\
2.0,-0.41510798897088297,-0.9093100097444322:\
2.5,-0.8000115470733413,-0.5991083419615396:\
3.0,-0.9891662142829148,-0.14244111088422928:\
3.5,-0.9363494234792721,0.3489685652606017:\
4.0,-0.6545300513139687,0.7549236989922106:\
4.5,-0.2126840278079185,0.9761531666722532:\
5.0,0.2810876700427761,0.9585871830343915:\
5.5,0.7060067356321447,0.7065722640487477:\
6.0,0.9581603294088602,0.28179586882321184:\
6.5,0.9759126845683772,-0.21181326254637473:\
7.0,0.7549711833099223,-0.6535130297883065:\
7.5,0.34942419607915476,-0.9352827832491797:\
8.0,-0.14150020322701534,-0.9882404948790053:\
8.5,-0.5977130717323988,-0.7994817952615989:\
9.0,-0.9076405091196682,-0.41522437449061833:\
9.5,-0.9955107720822968,0.07050843613198066:\
10.0,-0.8398791092277333,0.5388940756240107".split(":")

    inFile = open("spring1.dat")
    nI = 0
    bError = False
    for strLine in inFile:
        if strSpring1[nI] != strLine.strip():
            print("ERROR: ", strLine)
            bError = True
        nI += 1
    if not bError and nI == 21:
        print("Wave equation test passed")
    else:
        print("ERROR: Expected 21 lines in data file, only got: ", nI)
        
elif __name__ == "__main__" and nTest == 1:

    class Displacement:
        def __init__(self, nIndex):
            self.nVelocityIndex = nIndex+1
            
        def __call__(self, fTime, vecY):
            return vecY[self.nVelocityIndex]
            
    class Acceleration:
        def __init__(self, nIndex, nEnd):
            self.nIndex = nIndex
            self.nEnd = nEnd
            self.nLower = 0
            self.nUpper = 0
            if nEnd != -1:
                self.nLower = nIndex - 2
            if nEnd != 1:
                self.nUpper = nIndex + 2
            
        def __call__(self, fTime, vecY):

            fXM = 0.0
            fXP = 0.0
            if self.nEnd != -1:
                fXM = vecY[self.nLower]
            if self.nEnd != 1:
                fXP = vecY[self.nUpper]
            return -5.4495912806539506*(2*vecY[self.nIndex]-fXM-fXP)

    lstVelocity = [0.00069152891625033186,
                            0.00087553938831428561,
                            -0.0015670683045646175
                            ]

    pSolver = RungeKutta(10)
    nAtoms = 3
    for nI in range(0, nAtoms):
        if nI == 0:
            nEnd = -1
        elif nI == nAtoms-1:
            nEnd = 1
        else:
            nEnd = 0
        pSolver.addEquation(Displacement(nI*2), 0)
        pSolver.addEquation(Acceleration(nI*2+1, nEnd), lstVelocity[nI])
        
    print(len(pSolver.getValues()))
            
    class Output(object):
        
        def __init__(self, strFilename):
            self.outFile = open(strFilename, "w")
            self.fXMax = 0
            self.fVMax = 0
            
        def __call__(self, fTime, pSolver, bFinal):
            self.outFile.write(str(fTime))
            lstSum = [0, 0]
            nInd = 0
            for fValue in pSolver.vecY:
                self.outFile.write(","+str(fValue))
                lstSum[nInd%2] += fValue
                nInd += 1
            if abs(lstSum[0]) > self.fXMax:
                self.fXMax = abs(lstSum[0])
            if abs(lstSum[1]) > self.fVMax:
                self.fVMax = abs(lstSum[1])           
            self.outFile.write("\n")

    pOutput = Output("atoms.dat")
    pSolver.addAuxFunction(pOutput)
    
    pSolver.evolve()    # solve
    
    pOutput.outFile.close()
    print(pOutput.fXMax, pOutput.fVMax)
