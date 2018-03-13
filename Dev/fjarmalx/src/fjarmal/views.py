from django.shortcuts import render
from django.views.generic import View
import requests

# Create your views here.
def home(request):
    symbols = ['SKEL','EIK','REITIR','SIMINN','GRND',
                'SJOVA','N1','TM','VIS','VOICE','EIM',
                'EIM','REGINN','HAGA','ORIGO','ICEAIR'
                'MARL']

    Symbol1 = "N1"

    url = str.format("https://genius3p.livemarketdata.com/datacloud/Rest.ashx/NASDAQOMXNordicSharesEOD/EODPricesSDD?symbol={0}&fromdate=1.3.2017&todate=13.3.2018", Symbol1)

    #url = 'https://genius3p.livemarketdata.com/datacloud/Rest.ashx/NASDAQOMXNordicSharesEOD/EODPricesSDD?symbol=HAGA&fromdate=1.3.2017&todate=13.3.2018'
    url2 = 'http://apis.is/currency/m5'
    headers = {'Accept': 'text/json',
    'Authorization': 'GUSER-48e65cbe-2fef-49f3-8ffa-aec722e9564d'}

    response = requests.get(url, headers=headers)
    response2 = requests.get(url2)
    data = response.json()
    data2 = response2.json()

    return render(request, 'base.html', {
        # Respone for livemarketdata.com API
        'allData': data,
        'tradingDate': [i['trading_date'] for i in data],
        'officialLast': [i['official_last'] for i in data],
        # Respone for currency API
        'shortNames': [i['shortName' ] for i in data2['results']],
        'valueCurr': [i['value' ] for i in data2['results']],
    })

def market(request):
    url = 'https://genius3p.livemarketdata.com/datacloud/Rest.ashx/NASDAQOMXNordicSharesEOD/EODPricesSDD?symbol=HAGA&fromdate=1.3.2018&todate=13.3.2018'
    url2 = 'http://apis.is/currency/m5'
    headers = {'Accept': 'text/json',
    'Authorization': 'GUSER-48e65cbe-2fef-49f3-8ffa-aec722e9564d'}

    response = requests.get(url, headers=headers)
    response2 = requests.get(url2)
    data = response.json()
    data2 = response2.json()

    return render(request, 'market.html', {
        # Respone for livemarketdata.com API
        'officialLast': [i['official_last'] for i in data],
        # Respone for currency API
        'shortNames': [i['shortName' ] for i in data2['results']],
        'valueCurr': [i['value' ] for i in data2['results']],
    })

def about(request):
    return render(request, 'about.html')
