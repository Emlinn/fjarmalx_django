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


#Calculate individual returns
def avgRet(dailyRet):
	expR = dailyRet.mean()
	return expR

#Calculate portfolio risk and return
def portData(w, expR, C):
	
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
	

#Strategies - Hold the same portfolio.
def indexPort(data, dt, updateInterval, finalTime, CAP, commission, rf):
	#w = np.array([0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909])
	w = np.array([1])
	
	incDt = dt;
	update = 0;
	finalTime = int(finalTime/dt)

	#Initialize lists to store returns and trading cost
	ret = []; #Daily Return
	investRet = []; #Return on investment
	costOfTrading = []; 
	totalCost = CAP;
	costOfTrading.append(totalCost)
	
	
	for i in range(0,finalTime):
		priceData = data.iloc[0:dt, 12:13]
		#priceData = data.iloc[0:dt, 1:11]
		dailyReturns = logReturns(priceData)
		expReturns, sigma, corr, C = dataInfo(dailyReturns)
		portR, portStd = portData(w, expReturns, C)

		
		if update == updateInterval:
			totalCost = totalCost + tradingCost(w, w, CAP, commission)
			costOfTrading.append(totalCost)
			update = 0;	
		else:
			costOfTrading.append(totalCost)

		update = update + incDt;
		ret.append(portR)
		dt = dt + incDt;

	return (ret, costOfTrading);


#Strategies - Hold the min. var port. 
def minVarStrat(data, dt, updateInterval, finalTime, CAP, commission, rf):

	w = np.array([0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909])
	
	incDt = dt;
	update = 0;
	finalTime = int(finalTime/dt)

	ret = []; #Daily Return
	investRet = []; #Return on investment
	costOfTrading = []; 
	totalCost = CAP;
	costOfTrading.append(totalCost)

	for i in range(0,finalTime):
		priceData = data.iloc[0:dt, 1:12]
		dailyReturns = logReturns(priceData)
		expReturns, sigma, corr, C = dataInfo(dailyReturns)
		portR, portStd = portData(w, expReturns, C)
		
		if update == updateInterval:
			prevW = w;
			min_w, ERP, minSigma = minRiskPort(expReturns, sigma, C)
			min_w = np.asarray(min_w) #neccessary since minRiskPort returns a matrix
			min_w = min_w.flatten()
			w = min_w
			totalCost = totalCost + tradingCost(prevW, w, CAP, commission)
			costOfTrading.append(totalCost)
			update = 0;
		else:
			costOfTrading.append(totalCost)

		update = update + (incDt);
		ret.append(portR)
		dt = dt + incDt

	return (ret, costOfTrading);

def marketPortStrat(data, dt, updateInterval, finalTime, CAP, commission, rf):

	w = np.array([0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909])
	
	incDt = dt;
	update = 0;
	finalTime = int(finalTime/dt)

	ret = []; #Daily Return
	investRet = []; #Return on investment
	costOfTrading = []; 
	totalCost = CAP;
	costOfTrading.append(totalCost)

	for i in range(0,finalTime):
		priceData = data.iloc[0:dt, 1:12]
		dailyReturns = logReturns(priceData)
		expReturns, sigma, corr, C = dataInfo(dailyReturns)
		portR, portStd = portData(w, expReturns, C)
		
		if update == updateInterval:
			prevW = w;
			w_mp, r_mp, sigma_mp = marketPort(expReturns, rf, C)
			w_mp = np.asarray(w_mp) #neccessary since minRiskPort returns a matrix
			w_mp = w_mp.flatten()
			w = w_mp
			totalCost = totalCost + tradingCost(prevW, w, CAP, commission)
			costOfTrading.append(totalCost)
			update = 0;
		else:
			costOfTrading.append(totalCost)

		update = update + (incDt);
		ret.append(portR)
		dt = dt + incDt

	return (ret, costOfTrading);