#FUNCTIONS USED TO CALCULATE PORTFOLIO INFORMATION
#import libraries
import pandas as pd
import numpy as np
import math


def logReturns(data):
	dailyReturns = data.apply(lambda x: np.log(x) - np.log(x.shift(1)))
	return dailyReturns

def dataInfo(dailyReturns):
	expReturns = dailyReturns.mean()
	sigma = dailyReturns.std()
	corr = dailyReturns.corr()
	C = dailyReturns.cov()

	expReturns = expReturns.as_matrix()
	sigma = sigma.as_matrix()
	corr = corr.as_matrix()
	C = C.as_matrix()

	return (expReturns, sigma, corr, C)

def minRiskPort(r, sigma, C):

	e = np.ones(shape=(len(sigma),1))
	invC = np.linalg.inv(C)

	min_w = np.dot(invC, e) / np.dot(np.dot(e.T, invC), e)
	ERP = np.dot(r, min_w)
	minSigma = np.sqrt(np.dot(np.dot(min_w.T, C), min_w))

	return (min_w, ERP, minSigma)

def marketPort(expReturns, r_f, C):
	r = expReturns[np.newaxis, :].T
	e = np.ones(shape = (len(expReturns),1))
	invC = np.linalg.inv(C)

	w_mp = (np.dot(invC, (r - (r_f * e)))) / (np.dot(np.dot(e.T, invC), (r - (np.dot(r_f, e)))))
	sigma_mp = np.sqrt(np.dot(np.dot(w_mp.T, C), w_mp))
	r_mp = np.dot(r.T, w_mp)

	return (w_mp, r_mp, sigma_mp)

def requiredReturns(expReturns, C, r_c):
	invC = np.linalg.inv(C)
	e = np.ones(shape=(len(expReturns), 1))
	r = expReturns[np.newaxis, :].T

	A_numerator = np.dot(np.dot(invC, r), (np.dot(np.dot(e.T, invC), e))) - np.dot(np.dot(invC, e),np.dot(np.dot(e.T, invC), r))
	B_numerator = np.dot(np.dot(invC, e), (np.dot(np.dot(r.T, invC), r))) - np.dot(np.dot(invC, r), np.dot(np.dot(r.T, invC), e))
	AB_denomerator = np.dot((np.dot(np.dot(e.T, invC), e)), np.dot(np.dot(r.T, invC), r)) - np.dot(np.dot(np.dot(e.T, invC), r), np.dot(np.dot(r.T, invC), e))

	A = A_numerator / AB_denomerator
	B = B_numerator / AB_denomerator

	reqReturnsW = r_c*A+B
	ER = np.dot(r.T, reqReturnsW)
	stdDevMrx = np.sqrt(np.dot(np.dot(reqReturnsW.T, C), reqReturnsW))
	reqSigma = stdDevMrx.diagonal()

	return (reqReturnsW, ER, reqSigma)
