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
from .forms import StratForm

NOW = datetime.now()

DEFAULT_SYMBOLS = ['SKEL','EIK','REITIR','SIMINN','GRND','SJOVA','N1','TM','VIS','SYN','EIM','REGINN','HAGA','ORIGO','ICEAIR','MARL']
#DEFAULT_SYMBOLS = ['SJOVA','N1','TM','VIS','EIM','REGINN','HAGA','ICEAIR','MARL']

DEFAULT_FROMDATE = "1.1.2015"
DEFAULT_TODATE = NOW.strftime("%d.%m.%Y")
DEFAULT_FROMDATESTRAT = "1.1.2014" #1.1.2014
DEFAULT_TODATESTRAT = "1.1.2018" #1.1.2015
DEFAULT_LENGTH = 996 #995
HEADERS = {
    'Accept': 'text/json',
    'Authorization': 'GUSER-4d701a51-374b-437b-ad78-dbdaa0b2eb27'
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

    if Symbol == "SKEL":
        marketValue = "13.023.285.883"
        peRat = 11.38
    elif Symbol == "EIK":
        marketValue = "34.632.931.959"
        peRat = 8.57
    elif Symbol == "REITIR":
        marketValue = "64.923.765.413"
        peRat = 11.45
    elif Symbol == "SIMINN":
        marketValue = "40.766.708.918"
        peRat = 12.78
    elif Symbol == "GRND":
        marketValue = "63.206.006.497"
        peRat = 20.83
    elif Symbol == "SJOVA":
        marketValue = "23.865.687.966"
        peRat = 13.67
    elif Symbol == "N1":
        marketValue = "27.625.000.000"
        peRat = 14.37
    elif Symbol == "TM":
        marketValue = "23.701.086.282"
        peRat = 7.59
    elif Symbol == "VIS":
        marketValue = "30.506.595.952"
        peRat = 15.42
    elif Symbol == "SYN":
        marketValue = "20.632.326.590"
        peRat = 19.00
    elif Symbol == "REGINN":
        marketValue = "39.500.506.270"
        peRat = 10.43
    elif Symbol == "ORIGO":
        marketValue = "9.907.744.544"
        peRat = 29.33
    elif Symbol == "ICEAIR":
        marketValue = "64.826.538.996"
        peRat = 16.69
    elif Symbol == "MARL":
        marketValue = "263.955.203.606"
        peRat = 20.80

    tradeDate = [datetime.strptime(i['trading_date'], "%Y-%m-%dT%H:%M:%S").strftime("%d.%m.%Y") for i in data]

    return render(request, 'base.html', {
        'inputdata' : str(Symbol),
        # Respone for livemarketdata.com API
        'tradingDate' : json.dumps([datetime.strptime(i['trading_date'], "%Y-%m-%dT%H:%M:%S").strftime("%d.%m.%Y") for i in data]),
        'officialLast': [i['official_last'] for i in data],
        # Respone for currency API
        'shortNames': [i['shortName'] for i in data2['results']],
        'valueCurr': [i['value'] for i in data2['results']],
        'dailyChange' : float(str(round(percenteChange, 2))),
        'marketV' : marketValue,
        'peRatio' : peRat,
    })

def market(request):
    if request.method == 'POST':
        form = RiskFreeRateForm(request.POST)
        if form.is_valid:
            return HttpResponseRedirect('/marketport/?rate={0}'.format(request.POST.get('rate')))
    else:
        #stockDf is a dictionary
        stockDf = getStocksForStrat()
        ticker = stockDf.keys()
        stockTicker = list(ticker)

        #Convert dictionary to pandas dataframe
        df = pd.DataFrame.from_dict(stockDf, orient = 'columns')

        #df = pd.read_csv('fjarmal/data.csv', encoding = 'latin-1')
        priceData = df.iloc[200:996, 0:16]

        #RISK_FREE_RATE = 0.00002
        RISK_FREE_RATE = 2/100000.0

        #pdb.set_trace() DEBUGGER
        r_f = request.GET.get('rate', RISK_FREE_RATE)
        r_f = float(r_f)
        r_f = r_f/10000.0 #ATH PASSA HVERJU ER VERIÐ AÐ DEILA MEÐ !!!
        #r_f = 0.00001

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
        minW = min_w.tolist()
        ERP = ERP.tolist()
        minStdDev = minSigma.tolist()
        mpW = w_mp.tolist()
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
            'minW':minW,
            'minStdDev' : minStdDev,
            'rMP' : rMP,
            'stdDevMP' : stdDevMP,
            'mpW':mpW,
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
        form = StratForm(request.POST)
        if form.is_valid:
            #return HttpResponseRedirect('/marketport/?rate={0}&capital={1}'.format(request.POST.get(newComission,newCapital)))
            return HttpResponseRedirect('/strat/?comission={0}&capital={1}&rate={2}&pick_strat={3}&pick_date={4}'.format(request.POST.get('comission'),request.POST.get('capital'),request.POST.get('rate'),request.POST.get('pick_strat'),request.POST.get('pick_date')))
    else:
        dt = 5
        DEFAULT_INTERVAL = 100 #User input
        INITIAL_CAPITAL = 1000000 #User input
        COMISSION = 0.025 #User input
        DEFAULT_STRAT = 0
        DEFAULT_RF = 0.0002 #User input

        comm = request.GET.get('comission', COMISSION)
        comm = float(comm)
        initCAP = request.GET.get('capital', INITIAL_CAPITAL)
        initCAP = int(initCAP)
        rf = request.GET.get('rate', DEFAULT_RF)
        rf = float(rf)
        strat = request.GET.get('pick_strat', DEFAULT_STRAT)
        updateInterval = request.GET.get('pick_date', DEFAULT_INTERVAL)
        updateInterval = int(updateInterval)

        form = StratForm()

        #Strategies Functions
        if strat == 0:
            return render(request, 'strat.html', {
                'stratForm' : form,
                'whatStrat' : strat,
            })
        if strat == "strat1":
            stockData = getStocksForStrat()
            df = pd.DataFrame.from_dict(stockData, orient = 'columns') #Max. 830 rows and 9 columns for current selection
            indexDf =  pd.read_csv('fjarmal/index.csv', encoding = 'latin-1')
            priceData = df.iloc[300:600, 0:16]
            indexData = indexDf.iloc[300:600, 1:2]

            comm = request.GET.get('comission', COMISSION)
            comm = float(comm)
            initCAP = request.GET.get('capital', INITIAL_CAPITAL)
            initCAP = int(initCAP)
            rf = request.GET.get('rate', DEFAULT_RF)
            rf = float(rf)
            strat = request.GET.get('pick_strat', DEFAULT_STRAT)
            updateInterval = request.GET.get('pick_date', DEFAULT_INTERVAL)
            updateInterval = int(updateInterval)

            indexCAP = indexStrat(indexData, dt, updateInterval, initCAP, comm, rf)
            stratW, stratRet, stratCAP, stratCAPwCost, tradingCost = momentumStrat(priceData, dt, updateInterval, initCAP, comm, rf)
            stratW = stratW.tolist()
            return render(request, 'strat.html', {
                'dt' : dt,
                'indexCAP' : indexCAP,
                'stratForm' : form,
                'INITCAPAS' : initCAP,
                'stratW' : stratW,
                'stratRet' : stratRet,
                'stratCAP' : stratCAP,
                'stratCAPwCost' : stratCAPwCost,
                'tradingCost' : tradingCost
            })
        elif strat == "strat2":
            stockData = getStocksForStrat()
            df = pd.DataFrame.from_dict(stockData, orient = 'columns') #Max. 830 rows and 9 columns for current selection
            indexDf =  pd.read_csv('fjarmal/index.csv', encoding = 'latin-1')
            priceData = df.iloc[300:900, 0:16]
            indexData = indexDf.iloc[300:900, 1:2]

            comm = request.GET.get('comission', COMISSION)
            comm = float(comm)
            initCAP = request.GET.get('capital', INITIAL_CAPITAL)
            initCAP = int(initCAP)
            rf = request.GET.get('rate', DEFAULT_RF)
            rf = float(rf)
            strat = request.GET.get('pick_strat', DEFAULT_STRAT)
            updateInterval = request.GET.get('pick_date', DEFAULT_INTERVAL)
            updateInterval = int(updateInterval)

            indexCAP = indexStrat(indexData, dt, updateInterval, initCAP, comm, rf)
            stratW, stratRet, stratCAP, stratCAPwCost, tradingCost = momentumStratShort(priceData, dt, updateInterval, initCAP, comm, rf)
            stratW = stratW.tolist()
            return render(request, 'strat.html', {
                'dt' : dt,
                'indexCAP' : indexCAP,
                'stratForm' : form,
                'INITCAPAS' : initCAP,
                'stratW' : stratW,
                'stratRet' : stratRet,
                'stratCAP' : stratCAP,
                'stratCAPwCost' : stratCAPwCost,
                'tradingCost' : tradingCost
            })
        elif strat == "comp":
            stockData = getStocksForStrat()
            df = pd.DataFrame.from_dict(stockData, orient = 'columns') #Max. 830 rows and 9 columns for current selection
            indexDf =  pd.read_csv('fjarmal/index.csv', encoding = 'latin-1')
            priceData = df.iloc[300:900, 0:16]

            comm = request.GET.get('comission', COMISSION)
            comm = float(comm)
            initCAP = request.GET.get('capital', INITIAL_CAPITAL)
            initCAP = int(initCAP)
            rf = request.GET.get('rate', DEFAULT_RF)
            rf = float(rf)
            strat = request.GET.get('pick_strat', DEFAULT_STRAT)
            updateInterval = request.GET.get('pick_date', DEFAULT_INTERVAL)
            updateInterval = int(updateInterval)

            updateInterval = 10;
            updateMidInterval = 50;
            updateLongInterval = 100;

            indexCAP = indexStrat(indexData, dt, updateInterval, initCAP, comm, rf)
            stratW, stratRet, stratCAP, stratCAPwCost, tradingCost = momentumStrat(priceData, dt, updateInterval, initCAP, comm, rf)
            stratMidW, stratMidRet, stratMidCAP, stratMidCAPwCost, tradingMidCost = momentumStrat(priceData, dt, updateMidInterval, initCAP, comm, rf)
            stratLongW, stratLongRet, stratLongCAP, stratLongCAPwCost, tradingLongCost = momentumStrat(priceData, dt, updateLongInterval, initCAP, comm, rf)
            stratW = stratW.tolist()
            stratMidW = stratMidW.tolist()
            stratLongW = stratLongW.tolist()
            return render(request, 'strat.html', {
                
                'dt' : dt,
                'indexCAP' : indexCAP,
                'stratW' : stratW,
                'stratCAP' : stratCAP,
                'stratCAPwCost' : stratCAPwCost,
                'tradingCost' : tradingCost,
                'stratMidW' : stratMidW,
                'stratMidCAP' : stratMidCAP,
                'stratMidCAPwCost' : stratMidCAPwCost,
                'tradingMidCost' : tradingMidCost,
                'stratLongW':stratLongW,
                'stratLongCAP':stratLongCAP,
                'stratLongCAPwCost':stratLongCAPwCost,
                'tradingLongCost':tradingLongCost

            })


def about(request):
     return render(request, 'about.html')

def data(request):
    return render(request, 'data.html')
