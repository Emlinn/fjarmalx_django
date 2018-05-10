from django import forms
from django.utils.safestring import mark_safe

STRAT_CHOICES= [
    ('strat1', 'Strategy 1'),
    ('strat2', 'Strategy 2'),
    ('strat3', 'Strategy 3'),
    ('strat4', 'Strategy 4')
    ]

COMP_CHOICES= [
    ('comp', 'Interval'),
    ]


DATE_CHOICES = [
    (10, '10 days'),
    (20, '20 days'),
    (50, '50 days'),
    (100, '100 days'),
]

class RiskFreeRateForm(forms.Form):
    rate = forms.FloatField(label='Risk Free Rate (%) :', min_value=0, max_value=100)

class StratForm(forms.Form):
    comission = forms.FloatField(label='Comission (%):', min_value=0, max_value=100)
    capital =  forms.IntegerField(label=mark_safe('Capital '), min_value=0, max_value=100000000)
    rate = forms.FloatField(label=mark_safe('Risk Free Rate (%)'), min_value=0, max_value=100)
    pick_strat = forms.CharField(label=mark_safe('Strategy '),widget=forms.Select(choices=STRAT_CHOICES))
    pick_date = forms.CharField(label=mark_safe('Update Interval '),widget=forms.Select(choices=DATE_CHOICES))

class CompForm(forms.Form):
    comission = forms.FloatField(label='Comission:', min_value=0, max_value=100)
    capital =  forms.IntegerField(label=mark_safe('Capital '), min_value=0, max_value=100000000)
    pick_strat = forms.CharField(label=mark_safe('Compare '),widget=forms.Select(choices=COMP_CHOICES))
    pick_date = forms.CharField(label=mark_safe('Update Interval '),widget=forms.Select(choices=DATE_CHOICES))
