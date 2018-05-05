#FUNCTION USED FOR MOMENTUM TRADING
from fjarmal.calc import *
import pandas as pd
import numpy as np
import math

#Initialize weights
def initWeights(expR):
	N = len(expR)
	indW = 1.0/N;
	w = np.ones(N)
	w = w * indW
	return w

def dailyReturns(data):
    numRow = data.shape[0]
    numCol = data.shape[1]

    dReturns = pd.DataFrame(0, index = range(data.shape[0]), columns=range(data.shape[1]))

    for j in range(0, numCol):
        for i in range(1, numRow):
            dReturns.loc[i, j] = math.log(data.iloc[i][j] / data.iloc[i - 1][j])

    return dReturns

#Calculate individual returns
def avgRet(dailyRet):
	avgR = dailyRet.mean()
	return avgR

#Calculate portfolio risk and return
def portRet(w, expR, C):
	
	portR = expR @ w;
	portStd = np.sqrt(w.T @ C @ w);
	return (portR, portStd)



#Calculate Sharpe Ratio
def sharpeRatio(portR, portStd, rf):
	SR = (portR - rf)/portStd;
	return SR;


#Calculate trading cost
def tradingCost(prevW, updateW, inv, commission):
	diffW = np.absolute(updateW - prevW);
	sumW = np.sum(diffW);

	totalCap = sumW * inv;
	totalCost = totalCap * commission;

	return round(totalCost,2);


#Momentum strategy - 1: For each updating period we sell the three lowest performing stocks
#and invest in the three highest performing stocks. 
def momentumStrat(data, dt, updateInterval, initCAP, comm, rf):

	#Var. for dt return calculations
	incDt = dt
	startCounter = 0
	endCounter = dt

	#Var. for updating calculations
	startUpdate = 0
	endUpdate = updateInterval
	updateCounter = 0

	finalTime = int(300/dt)
	intervalArr = [] #Store dt returns
	updateArr = [[0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,]] #Store weights for each interval
	wPlotArr = [[0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,]]

	CAP = initCAP
	capArr = []

	CAPwCost = initCAP
	capWcostArr = [];

	tradeCostSum = 0

	wCounter = 0;

	w = np.array([0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,0.0625,])


	for i in range(0,finalTime):
		if updateCounter == updateInterval:
			updatePrice = data.iloc[startUpdate:endUpdate, 0:16]
			updateRet = dailyReturns(updatePrice)
			updateAvgRet = avgRet(updateRet)

			#Updating strategy calculations
			minR = updateAvgRet.nsmallest(3)
			maxR = updateAvgRet.nlargest(3)
			minIndex = minR.index.values
			maxIndex = maxR.index.values

			wArr = []
			wSum = 0
			wDist = 0

			for k in minIndex:
				wArr.append(w[k])
				w[k] = 0;

			wSum = sum(wArr)
			wDist = wSum/3.0

			for j in maxIndex:
				tmpW = w[j] + wDist
				w[j] = tmpW

			updateArr = np.vstack([updateArr, w])
			tradeCost = tradingCost(updateArr[wCounter], updateArr[wCounter+1], CAP, comm)
			tradeCostSum = tradeCostSum - tradeCost

			#Update counters
			startUpdate = startUpdate + updateInterval
			endUpdate = endUpdate + updateInterval
			updateCounter = 0
			wCounter = wCounter + 1

		intervalPrice = data.iloc[startCounter:dt, 0:16]
		intervalRet = dailyReturns(intervalPrice)
		intervalAvgRet, intervalStd, intervalCorr, intervalC = dataInfo(intervalRet)
		intervalPortAvgRet, intervalPortStdDev = portRet(w, intervalAvgRet, intervalC)
		CAP = CAP + (CAP*intervalPortAvgRet)
		CAPwCost = CAP + tradeCostSum

		CAP = round(CAP,2)
		CAPwCost = round(CAPwCost,2)

		wPlotArr = np.vstack([wPlotArr, w])
		intervalArr.append(intervalPortAvgRet)
		capArr.append(CAP)
		capWcostArr.append(CAPwCost)

		#Update Counters
		updateCounter = updateCounter + incDt
		startCounter = startCounter + incDt
		dt = dt + incDt


	return (wPlotArr, intervalArr, capArr, capWcostArr)



#def momentumStratShort(data, dt, updateInterval, initCAP, comm, rf):






