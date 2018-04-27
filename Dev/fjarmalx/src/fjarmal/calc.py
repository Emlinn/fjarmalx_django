#FUNCTIONS USED TO CALCULATE PORTFOLIO INFORMATION
#import libraries
import pandas as pd
import numpy as np
import math
from scipy.stats import norm

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

	min_w = (invC @ e)/(e.T @ invC @ e)
	ERP = r @ min_w
	minSigma = np.sqrt(min_w.T @ C @ min_w)
	return (min_w, ERP, minSigma)

def marketPort(expReturns, r_f, C):
	r = expReturns[np.newaxis, :].T
	e = np.ones(shape = (len(expReturns),1))
	invC = np.linalg.inv(C)

	w_mp = (invC @ (r - (r_f * e)))/(e.T @ invC @ (r - r_f * e))
	sigma_mp = np.sqrt(w_mp.T @ C @ w_mp)
	r_mp = r.T @ w_mp

	return (w_mp, r_mp, sigma_mp)

def requiredReturns(expReturns, C, r_c):
	invC = np.linalg.inv(C)
	e = np.ones(shape=(len(expReturns), 1))
	r = expReturns[np.newaxis, :].T

	A = (invC @ r @ (e.T @ invC @ e) - invC @ e @ (e.T @ invC @ r))/((e.T @ invC @ e) @ (r.T @ invC @ r) - (e.T @ invC @ r) @ (r.T @ invC @ e))
	B = (invC @ e @ (r.T @ invC @ r) - invC @ r @ (r.T @ invC @ e))/((e.T @ invC @ e) @ (r.T @ invC @ r) - (e.T @ invC @ r) @ (r.T @ invC @ e))

	reqReturnsW = r_c*A+B
	ER = r.T @ reqReturnsW
	stdDevMrx = np.sqrt(reqReturnsW.T @ C @ reqReturnsW)
	reqSigma = stdDevMrx.diagonal()

	return (reqReturnsW, ER, reqSigma)

def CML(std, r_mp, r_f, std_mp):
	adjStd = np.insert(std, 0, 0)
	grad = (r_mp - r_f)/std_mp
	cml = r_f + adjStd * grad;
	return (adjStd, cml);

def ValueAtRisk(conf, C, w, V, dt):
	alpha = norm.ppf(1-conf);
	std_p = np.sqrt(w.T @ C @ w)
	VaR = alpha * std_p * V * np.sqrt(dt)

	return VaR

#def putOption()
