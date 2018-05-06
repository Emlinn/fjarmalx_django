from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from fjarmal.calc import *
from fjarmal.moment import *
import requests
import pandas as pd
from pandas import Series
import numpy as np
import pdb
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.urls import reverse

from .forms import RiskFreeRateForm

NOW = datetime.now()

DEFAULT_SYMBOLS = ['SKEL','EIK','REITIR','SIMINN','GRND','SJOVA','N1','TM','VIS','SYN','EIM','EIM','REGINN','HAGA','ORIGO','ICEAIR','MARL']
#DEFAULT_SYMBOLS = ['SJOVA','N1','TM','VIS','EIM','REGINN','HAGA','ICEAIR','MARL']

DEFAULT_FROMDATE = "1.1.2015"
DEFAULT_TODATE = NOW.strftime("%d.%m.%Y")
DEFAULT_FROMDATESTRAT = "1.1.2014" #1.1.2014
DEFAULT_TODATESTRAT = "1.1.2018" #1.1.2015
DEFAULT_LENGTH = 996 #995
HEADERS = {
    'Accept': 'text/json',
    'Authorization': 'GUSER-8d6f7343-927b-4453-bd3d-087f525e1bc1'
    }
SINGLE_STOCK_URL = "https://genius3p.livemarketdata.com/datacloud/Rest.ashx/NASDAQOMXNordicSharesEOD/EODPricesSDD?symbol={0}&fromdate={1}&todate={2}"

def getStocks():
    stocks = { key: [] for key in DEFAULT_SYMBOLS }

    for symb in DEFAULT_SYMBOLS:
        response = requests.get(SINGLE_STOCK_URL.format(symb, DEFAULT_FROMDATE, DEFAULT_TODATE), headers=HEADERS)
        data = response.json()
        stocks[symb] = [ i['official_last'] for i in data ]

    return stocks

def getStocksForStrat():
    stocks = { key: [] for key in DEFAULT_SYMBOLS }

    for symb in DEFAULT_SYMBOLS:
        response = requests.get(SINGLE_STOCK_URL.format(symb, DEFAULT_FROMDATESTRAT, DEFAULT_TODATESTRAT), headers=HEADERS)

        company_stocks = [ i['official_last'] for i in response.json() ]

        pad_length = DEFAULT_LENGTH - len(company_stocks)
        padding = []
        if pad_length > 0:
            padding += [0] * pad_length

        stocks[symb] = padding + company_stocks

    return stocks

# Create your views here.
def home(request, input_symbol=None):

    if input_symbol:
        Symbol = input_symbol
    else:
        Symbol = "SKEL"

    url = SINGLE_STOCK_URL.format(Symbol, DEFAULT_FROMDATE, DEFAULT_TODATE)
    url2 = 'http://apis.is/currency/m5'

    response = requests.get(url, headers=HEADERS)
    response2 = requests.get(url2)
    data = response.json()
    data2 = response2.json()

    lastElement = [i['official_last'] for i in data][-1] - [i['official_last'] for i in data][-2]
    percenteChange = (lastElement/[i['official_last'] for i in data][-2]*100)

    return render(request, 'base.html', {
        'inputdata' : str(Symbol),
        # Respone for livemarketdata.com API
        'tradingDate' : json.dumps([datetime.strptime(i['trading_date'], "%Y-%m-%dT%H:%M:%S").strftime("%d.%m.%Y") for i in data]),
        'officialLast': [i['official_last'] for i in data],
        # Respone for currency API
        'shortNames': [i['shortName'] for i in data2['results']],
        'valueCurr': [i['value'] for i in data2['results']],
        'dailyChange' : float(str(round(percenteChange, 2))),
    })

def market(request):
    if request.method == 'POST':
        form = RiskFreeRateForm(request.POST)
        if form.is_valid:
            #newRate = form.cleaned_data['rate']
            #return HttpResponseRedirect('/marketport/?rate={0}'.format(newRate))
            return HttpResponseRedirect('/marketport/?rate={0}'.format(request.POST.get('rate')))
    else:

        #stockDf is a dictionary
        stockDf = getStocksForStrat()
        ticker = stockDf.keys()
        stockTicker = list(ticker)

        #Convert dictionary to pandas dataframe
        df = pd.DataFrame.from_dict(stockDf, orient = 'columns')

        #df = pd.read_csv('fjarmal/data.csv', encoding = 'latin-1')
        priceData = df.iloc[0:996, 0:16]

        RISK_FREE_RATE = 0.0002

        #pdb.set_trace() DEBUGGER
        #r_f = request.GET.get('rate', RISK_FREE_RATE)
        #r_f = float(r_f)
        r_f = 0.00001

        # Taka user input i thetta
        r_c = np.linspace(0.0003,0.004,num=20)

    

        #Calculate neccessary data
        dailyRet, yearlyRet = logReturns(priceData)
        expRet, sigma, corr, C = dataInfo(dailyRet)
        min_w, ERP, minSigma = minRiskPort(expRet, sigma, C)
        w_mp, r_mp, sigma_mp = marketPort(expRet, r_f, C)
        reqReturnsW, ER, reqSigma = requiredReturns(expRet, C, r_c)
        adjStdDev, capitalMarketLine = CML(r_mp, r_f, sigma_mp)

        #Constrained efficient frontier
        restRet, restStdDev = quadOpt(expRet, r_c, C)
      
        #Convert to list
        R = expRet.tolist()
        stdDev = sigma.tolist()
        ERP = ERP.tolist()
        minStdDev = minSigma.tolist()
        rMP = r_mp.tolist()
        stdDevMP = sigma_mp.tolist()
        reqER = ER.tolist()
        reqStdDev = reqSigma.tolist()
        capMarketLine = capitalMarketLine.tolist()
        cmlStdDev = adjStdDev.tolist()

        form = RiskFreeRateForm()
 
        return render(request, 'market.html', {
            # Respone for livemarketdata.com API
            'stockTicker' : stockTicker,
            'R' : R,
            'stdDev' : stdDev,
            'ERP' : ERP,
            'minStdDev' : minStdDev,
            'rMP' : rMP,
            'stdDevMP' : stdDevMP,
            'reqRet' : reqER[0],
            'reqStdDev' : reqStdDev,
            'CML' : capMarketLine[0],
            'cmlStdDev' : cmlStdDev,
            'restR' : restRet,
            'restStdDev' : restStdDev,
            'rateForm': form
        })
        

def strat(request):
    if request.method == 'POST':
        form = RiskFreeRateForm(request.POST)
        if form.is_valid:
            #newRate = form.cleaned_data['rate']
            #return HttpResponseRedirect('/marketport/?rate={0}'.format(newRate))
            return HttpResponseRedirect('/marketport/?rate={0}'.format(request.POST.get('rate')))
    else:
        
        stockData = getStocksForStrat()
        df = pd.DataFrame.from_dict(stockData, orient = 'columns') #Max. 830 rows and 9 columns for current selection
        indexDf =  pd.read_csv('fjarmal/index.csv', encoding = 'latin-1')
        priceData = df.iloc[300:900, 0:16]
        indexData = indexDf.iloc[300:900, 1:2]

      

        dt = 5
        updateInterval = 100; #User input 
        initCAP = 1000000 #User input
        comm = 0.025 #User input
        rf = 0.0002; #User input

        #Strategies Functions 
        indexCAP = indexStrat(indexData, dt, updateInterval, initCAP, comm, rf)
        #stratW, stratRet, stratCAP, stratCAPwCost = momentumStrat(priceData, dt, updateInterval, initCAP, comm, rf)
        stratW, stratRet, stratCAP, stratCAPwCost = momentumStratShort(priceData, dt, updateInterval, initCAP, comm, rf)
        stratW = stratW.tolist()
    

        return render(request, 'strat.html', {
            'dt' : dt,
            'indexCAP' : indexCAP,
            'stratW' : stratW,
            'stratRet' : stratRet,
            'stratCAP' : stratCAP,
            'stratCAPwCost' : stratCAPwCost
        })

def about(request):
     return render(request, 'about.html')

def data(request):
    return render(request, 'data.html')
