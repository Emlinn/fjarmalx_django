from django import forms
from django.utils.safestring import mark_safe

STRAT_CHOICES= [
    ('strat1', 'Strategy 1'),
    ('strat2', 'Strategy 2'),
    ('strat3', 'Strategy 3'),
    ]

class RiskFreeRateForm(forms.Form):
    rate = forms.FloatField(label='Risk Free Rate:', min_value=0, max_value=1)

class StratForm(forms.Form):
    comission = forms.FloatField(label='Comission:', min_value=0, max_value=1)
    capital =  forms.IntegerField(label=mark_safe('Capital '), min_value=0, max_value=100000000)
    rate = forms.FloatField(label=mark_safe('Risk Free Rate'), min_value=0, max_value=1)
    pick_strat = forms.CharField(label=mark_safe('Strategy '),widget=forms.Select(choices=STRAT_CHOICES))
