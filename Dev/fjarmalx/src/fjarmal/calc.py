#FUNCTIONS USED TO CALCULATE PORTFOLIO INFORMATION
#import libraries
import pandas as pd
import numpy as np
import math
from scipy.stats import norm
from numpy import array
import cvxopt as opt
from cvxopt import matrix, solvers

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

	w_mp = (invC @ (r - (r_f * e)))/(e.T @ invC @ (r - r_f * e));
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

def CML(r_mp, r_f, std_mp):
	adjStd = np.linspace(0,0.04, num = 50)
	grad = (r_mp - r_f)/std_mp
	cml = r_f + adjStd * grad;
	return (adjStd, cml);

def ValueAtRisk(conf, C, w, V, dt):
	alpha = norm.ppf(1-conf);
	std_p = np.sqrt(w.T @ C @ w)
	VaR = alpha * std_p * V * np.sqrt(dt)	

	return VaR

def quadOpt(expReturns, r_c, C):
	#CVXOPT SOLVER FOR QUADRADIC PROGRAMMING
	n = len(expReturns)
	r_min = 0.0010
	avg_ret = opt.matrix(expReturns)

	#Objective func.
	P = opt.matrix(C)
	q = matrix([0.0 for i in range(n)])

	#Inequality constraints
	G = matrix(np.concatenate((-np.transpose(np.array(avg_ret)), -np.identity(n)), 0))

	#Equality constraints
	A = opt.matrix(1.0, (1,n))
	b = opt.matrix(1.0)

	opts = {'show_progress' : False}
	rArr = []
	sArr = []

	for i in r_c:
		try:
			r_min = opt.matrix(i)
			h = matrix(np.concatenate((-np.ones((1, 1)) * r_min, np.zeros((n, 1))), 0))
			sol = solvers.qp(P, q, G, h, A, b, options=opts)
			optSol = sol['x']
			ret = array(avg_ret.T*optSol)
			sig = np.sqrt(optSol.T*P*optSol)
			rArr.append(ret)
			sArr.append(sig)
		except ValueError:
			break;

	restRet = []
	restStdDev = []

	for i in range(len(rArr)):
		restRet.append(rArr[i][0][0])
		restStdDev.append(sArr[i][0][0])

	return (restRet, restStdDev)



	
