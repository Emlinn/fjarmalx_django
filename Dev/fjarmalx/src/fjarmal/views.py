from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from fjarmal.calc import *
import requests
import pandas as pd
import numpy as np
import pdb
from django.urls import reverse

from .forms import RiskFreeRateForm

DEFAULT_SYMBOLS = ['SKEL','EIK','REITIR','SIMINN','GRND',
                    'SJOVA','N1','TM','VIS','EIM',
                    'EIM','REGINN','HAGA','ORIGO','ICEAIR',
                    'MARL']
DEFAULT_FROMDATE = "1.1.2017"
DEFAULT_TODATE = "1.3.2018"
DEFAULT_FROMDATESTRAT = "1.1.2014"
DEFAULT_TODATESTRAT = "1.1.2015"
DEFAULT_LENGTH = 995
HEADERS = {
    'Accept': 'text/json',
    'Authorization': 'GUSER-276cccd6-5e34-49f5-b228-518fd735e829'
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


    return render(request, 'base.html', {
        'inputdata' : str(Symbol),
        # Respone for livemarketdata.com API
        'tradingDate': [i['trading_date'] for i in data],
        'officialLast': [i['official_last'] for i in data],
        # Respone for currency API
        'shortNames': [i['shortName'] for i in data2['results']],
        'valueCurr': [i['value'] for i in data2['results']],
    })

def market(request):
    if request.method == 'POST':
        form = RiskFreeRateForm(request.POST)
        if form.is_valid:
            #newRate = form.cleaned_data['rate']
            #return HttpResponseRedirect('/marketport/?rate={0}'.format(newRate))
            return HttpResponseRedirect('/marketport/?rate={0}'.format(request.POST.get('rate')))
    else:

        RISK_FREE_RATE = 0.000005

        #pdb.set_trace() DEBUGGER

        r_f = request.GET.get('rate', RISK_FREE_RATE)
        r_f = float(r_f)

        V = 1000000
        dt = 1

        # Taka user input i thetta
        #r_f = 0.000005
        r_c = np.linspace(0.0001,0.01,num=40)

        #stockDf is a dictionary
        stockDf = getStocks()
        ticker = stockDf.keys()

        #Convert dictionary to pandas dataframe
        df = pd.DataFrame.from_dict(stockDf, orient = 'columns')


        #Calculate neccessary data
        dailyReturns = logReturns(df)
        expReturns, sigma, corr, C = dataInfo(dailyReturns)
        min_w, ERP, minSigma = minRiskPort(expReturns, sigma, C)
        w_mp, r_mp, sigma_mp = marketPort(expReturns, r_f, C)
        reqReturnsW, ER, reqSigma = requiredReturns(expReturns, C, r_c)
        adjStd, capitalMarketLine = CML(sigma, r_mp, r_f, sigma_mp)
        VaR = ValueAtRisk(0.95, C, min_w, V, dt)

        #Convert to list
        #stockTick = ticker.tolist()
        R = expReturns.tolist()
        stdDev = sigma.tolist()
        ERP = ERP.tolist()
        minStdDev = minSigma.tolist()
        rMP = r_mp.tolist()
        sigmaMP = sigma_mp.tolist()
        reqER = ER.tolist()
        reqStdDev = reqSigma.tolist()
        capMarketLine = capitalMarketLine.tolist()
        cmlStd = adjStd.tolist()
        VaR_list = VaR.tolist()

        form = RiskFreeRateForm()

        return render(request, 'market.html', {
            # Respone for livemarketdata.com API
            'testData' : stockDf,
            'stockTicker' : ticker,
            'len' : len(stockDf['REITIR']),
            'R' : R,
            'sigma' : stdDev,
            'ERP' : ERP,
            'minStdDev' : minStdDev,
            'rMP' : rMP,
            'sigmaMP' : sigmaMP,
            'reqER' : reqER,
            'reqStdDev' : reqStdDev,
            'CML' : capMarketLine,
            'adjStd' : cmlStd,
            'VaR' : VaR_list,
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
        test = getStocksForStrat()
        return render(request, 'strat.html', {
            # Respone for livemarketdata.com API
            'testData' : len(test['HAGA']),
            #'rateForm': form
        })

def about(request):
     return render(request, 'about.html')

def data(request):
    return render(request, 'data.html')
